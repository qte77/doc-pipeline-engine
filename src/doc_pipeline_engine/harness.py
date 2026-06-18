# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Parallel diff harness: run anthropic_sdk and local legs on the same sample.

Extraction is shared between legs (Kreuzberg runs once); only the post-
extraction stages diverge. The DiffReport captures both legs' contracts,
timings, costs, eval reports, and a small set of comparative axes.

Usage (CLI):
    python -m doc_pipeline_engine.harness <sample_path> [--output-dir DIR]

Both ``anthropic_sdk`` and ``extract`` extras must be installed for real runs:
    uv sync --extra extract --extra render --extra anthropic_sdk --extra local-render
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from doc_pipeline_engine.render.formats import RenderArtifacts


@dataclass
class LegResult:
    """All artifacts and timings produced by one pipeline leg (anthropic_sdk or local)."""

    variant: str  # "anthropic_sdk" | "local"
    contracts: list[dict[str, Any]]  # all stage outputs in order
    artifacts: RenderArtifacts
    wall_times: dict[str, float]
    eval_report: dict[str, Any]


@dataclass
class DiffReport:
    """Side-by-side anthropic_sdk + local result over one sample, with comparative axes."""

    sample_path: str
    sample_sha256: str
    extraction_bundle: dict[str, Any]
    anthropic_sdk: LegResult
    local: LegResult
    axes: dict[str, float] = field(default_factory=dict)


def _time(fn: Any, *args: Any, **kwargs: Any) -> tuple[Any, float]:
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    return out, time.perf_counter() - t0


def _run_anthropic_sdk_leg(bundle: dict[str, Any], model: str) -> LegResult:
    from doc_pipeline_engine.stages.anthropic_sdk_analyze import analyze_anthropic_sdk
    from doc_pipeline_engine.stages.anthropic_sdk_eval import eval_anthropic_sdk
    from doc_pipeline_engine.stages.anthropic_sdk_normalize import normalize_anthropic_sdk
    from doc_pipeline_engine.stages.anthropic_sdk_render import render_anthropic_sdk

    times: dict[str, float] = {}
    canonical, times["normalize"] = _time(normalize_anthropic_sdk, bundle, model=model)
    report, times["analyze"] = _time(analyze_anthropic_sdk, canonical, model=model)
    artifacts, times["render"] = _time(render_anthropic_sdk, report, model=model)
    eval_report, times["eval"] = _time(eval_anthropic_sdk, bundle, canonical, report, artifacts)
    return LegResult(
        variant="anthropic_sdk",
        contracts=[canonical, report, eval_report],
        artifacts=artifacts,
        wall_times=times,
        eval_report=eval_report,
    )


def _run_local_leg(bundle: dict[str, Any]) -> LegResult:
    from doc_pipeline_engine.stages.local_analyze import analyze_local
    from doc_pipeline_engine.stages.local_eval import eval_local
    from doc_pipeline_engine.stages.local_normalize import normalize_local
    from doc_pipeline_engine.stages.local_render import render_local

    times: dict[str, float] = {}
    canonical, times["normalize"] = _time(normalize_local, bundle)
    report, times["analyze"] = _time(analyze_local, canonical)
    artifacts, times["render"] = _time(render_local, report)
    eval_report, times["eval"] = _time(eval_local, bundle, canonical, report, artifacts)
    return LegResult(
        variant="local",
        contracts=[canonical, report, eval_report],
        artifacts=artifacts,
        wall_times=times,
        eval_report=eval_report,
    )


def _compute_axes(anthropic_sdk: LegResult, local: LegResult) -> dict[str, float]:
    """Comparative axes between anthropic_sdk and local results."""
    anthropic_sdk_total = sum(anthropic_sdk.wall_times.values())
    local_total = sum(local.wall_times.values())
    return {
        "anthropic_sdk_total_seconds": anthropic_sdk_total,
        "local_total_seconds": local_total,
        "latency_ratio_anthropic_sdk_over_local": (
            anthropic_sdk_total / local_total if local_total > 0 else 0.0
        ),
    }


def _write_artifacts(out_dir: Path, sha: str, variant: str, art: RenderArtifacts) -> None:
    sub = out_dir / sha / variant
    sub.mkdir(parents=True, exist_ok=True)
    (sub / "summary.md").write_text(art.md)
    (sub / "summary.docx").write_bytes(art.docx)
    (sub / "summary.pdf").write_bytes(art.pdf)


def run_both(
    sample_path: Path,
    *,
    anthropic_sdk_model: str = "claude-opus-4-7",
    output_dir: Path | None = None,
) -> DiffReport:
    """Discover + extract the sample once, then run both legs and diff."""
    from doc_pipeline_engine.stages.discover import discover
    from doc_pipeline_engine.stages.extract import extract

    root = sample_path.parent
    manifest = discover(root, glob=sample_path.name)
    files = manifest["files"]
    if not files:
        raise FileNotFoundError(f"no files matched at {sample_path}")
    file_entry = files[0]
    bundle = extract(file_entry, root)

    anthropic_sdk = _run_anthropic_sdk_leg(bundle, model=anthropic_sdk_model)
    local = _run_local_leg(bundle)
    axes = _compute_axes(anthropic_sdk, local)

    report = DiffReport(
        sample_path=str(sample_path),
        sample_sha256=file_entry["sha256"],
        extraction_bundle=bundle,
        anthropic_sdk=anthropic_sdk,
        local=local,
        axes=axes,
    )

    if output_dir is not None:
        out = Path(output_dir)
        _write_artifacts(out, file_entry["sha256"], "anthropic_sdk", anthropic_sdk.artifacts)
        _write_artifacts(out, file_entry["sha256"], "local", local.artifacts)

    return report


def _to_json(report: DiffReport) -> dict[str, Any]:
    """Serialise DiffReport to a JSON-safe dict; artifact bytes omitted."""
    def leg(r: LegResult) -> dict[str, Any]:
        return {
            "variant": r.variant,
            "contracts": r.contracts,
            "wall_times": r.wall_times,
            "eval_report": r.eval_report,
            "artifacts": {"md_chars": len(r.artifacts.md),
                          "docx_bytes": len(r.artifacts.docx),
                          "pdf_bytes": len(r.artifacts.pdf)},
        }
    return {
        "sample_path": report.sample_path,
        "sample_sha256": report.sample_sha256,
        "extraction_bundle": report.extraction_bundle,
        "anthropic_sdk": leg(report.anthropic_sdk),
        "local": leg(report.local),
        "axes": report.axes,
    }


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run anthropic_sdk + local legs on one sample."
    )
    parser.add_argument("sample", type=Path, help="Path to a single sample file")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Write rendered md/docx/pdf artifacts under this dir")
    parser.add_argument("--anthropic-sdk-model", default="claude-opus-4-7")
    args = parser.parse_args(argv)
    report = run_both(
        args.sample,
        anthropic_sdk_model=args.anthropic_sdk_model,
        output_dir=args.output_dir,
    )
    json.dump(_to_json(report), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())


__all__ = ["DiffReport", "LegResult", "run_both"]
