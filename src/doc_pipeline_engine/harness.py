# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Parallel diff harness: run V1 and V2 legs on the same sample and diff.

Extraction is shared between legs (Kreuzberg runs once); only the post-
extraction stages diverge. The DiffReport captures both legs' contracts,
timings, costs, eval reports, and a small set of comparative axes.

Usage (CLI):
    python -m doc_pipeline_engine.harness <sample_path> [--output-dir DIR]

Both ``v1`` and ``extract`` extras must be installed for real runs:
    uv sync --extra extract --extra render --extra v1 --extra v2-render
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from doc_pipeline_engine.render.formats import RenderArtifacts


@dataclass
class LegResult:
    variant: str  # "v1" | "v2"
    contracts: list[dict[str, Any]]  # all stage outputs in order
    artifacts: RenderArtifacts
    wall_times: dict[str, float]
    eval_report: dict[str, Any]


@dataclass
class DiffReport:
    sample_path: str
    sample_sha256: str
    extraction_bundle: dict[str, Any]
    v1: LegResult
    v2: LegResult
    axes: dict[str, float] = field(default_factory=dict)


def _time(fn: Any, *args: Any, **kwargs: Any) -> tuple[Any, float]:
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    return out, time.perf_counter() - t0


def _run_v1_leg(bundle: dict[str, Any], v1_model: str) -> LegResult:
    from doc_pipeline_engine.stages.v1_analyze import analyze_v1
    from doc_pipeline_engine.stages.v1_eval import eval_v1
    from doc_pipeline_engine.stages.v1_normalize import normalize_v1
    from doc_pipeline_engine.stages.v1_render import render_v1

    times: dict[str, float] = {}
    canonical, times["normalize"] = _time(normalize_v1, bundle, model=v1_model)
    report, times["analyze"] = _time(analyze_v1, canonical, model=v1_model)
    artifacts, times["render"] = _time(render_v1, report, model=v1_model)
    eval_report, times["eval"] = _time(eval_v1, bundle, canonical, report, artifacts)
    return LegResult(
        variant="v1",
        contracts=[canonical, report, eval_report],
        artifacts=artifacts,
        wall_times=times,
        eval_report=eval_report,
    )


def _run_v2_leg(bundle: dict[str, Any]) -> LegResult:
    from doc_pipeline_engine.stages.v2_analyze import analyze_v2
    from doc_pipeline_engine.stages.v2_eval import eval_v2
    from doc_pipeline_engine.stages.v2_normalize import normalize_v2
    from doc_pipeline_engine.stages.v2_render import render_v2

    times: dict[str, float] = {}
    canonical, times["normalize"] = _time(normalize_v2, bundle)
    report, times["analyze"] = _time(analyze_v2, canonical)
    artifacts, times["render"] = _time(render_v2, report)
    eval_report, times["eval"] = _time(eval_v2, bundle, canonical, report, artifacts)
    return LegResult(
        variant="v2",
        contracts=[canonical, report, eval_report],
        artifacts=artifacts,
        wall_times=times,
        eval_report=eval_report,
    )


def _compute_axes(v1: LegResult, v2: LegResult) -> dict[str, float]:
    """Comparative axes between V1 and V2 results."""
    v1_total = sum(v1.wall_times.values())
    v2_total = sum(v2.wall_times.values())
    return {
        "v1_total_seconds": v1_total,
        "v2_total_seconds": v2_total,
        "latency_ratio_v1_over_v2": v1_total / v2_total if v2_total > 0 else 0.0,
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
    v1_model: str = "claude-opus-4-7",
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

    v1 = _run_v1_leg(bundle, v1_model=v1_model)
    v2 = _run_v2_leg(bundle)
    axes = _compute_axes(v1, v2)

    report = DiffReport(
        sample_path=str(sample_path),
        sample_sha256=file_entry["sha256"],
        extraction_bundle=bundle,
        v1=v1,
        v2=v2,
        axes=axes,
    )

    if output_dir is not None:
        out = Path(output_dir)
        _write_artifacts(out, file_entry["sha256"], "v1", v1.artifacts)
        _write_artifacts(out, file_entry["sha256"], "v2", v2.artifacts)

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
        "v1": leg(report.v1),
        "v2": leg(report.v2),
        "axes": report.axes,
    }


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run V1 + V2 legs on one sample.")
    parser.add_argument("sample", type=Path, help="Path to a single sample file")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Write rendered md/docx/pdf artifacts under this dir")
    parser.add_argument("--v1-model", default="claude-opus-4-7")
    args = parser.parse_args(argv)
    report = run_both(args.sample, v1_model=args.v1_model, output_dir=args.output_dir)
    json.dump(_to_json(report), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())


__all__ = ["DiffReport", "LegResult", "run_both"]
