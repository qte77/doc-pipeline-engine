#!/usr/bin/env python3
# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""External Anthropic SDK one-shot summarizer.

Sends one Claude call per sample with the system prompt assembled
from `external/PROMPT.md` + `docs/contracts.md` (inlined; see
ADR-0004's mitigation note on the SDK's lack of file-reading) +
optionally `.claude/rules/*.md` when `--config project`.

Output: ``outputs/<sha>/external/anthropic-{vanilla,project}/{summary.md,meta.json}``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROMPT_PATH = REPO_ROOT / "external" / "PROMPT.md"
CONTRACTS_PATH = REPO_ROOT / "docs" / "contracts.md"
RULES_DIR = REPO_ROOT / ".claude" / "rules"

MODEL_DEFAULT = "claude-opus-4-7"
MAX_TOKENS = 4096

# Anthropic Opus 4.x pricing (USD per million tokens, as of 2026-04).
# Update when pricing changes; cost capture is informational, not load-bearing.
PRICE_PER_MTOK_INPUT = 15.00
PRICE_PER_MTOK_OUTPUT = 75.00


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_contracts_md() -> str:
    """Inline `docs/contracts.md` into the system prompt.

    FIXME(sdk-no-file-reading): the Anthropic SDK has no native
    file-reading tool, so we hand-load contracts.md (~5KB) into every
    request. CC variants (CLI / SDK) reference the file by path
    instead — those agents read it on demand. When the SDK gains a
    Read-equivalent tool (or we wrap it with one), drop this inline
    and switch to reference-only.
    """
    return CONTRACTS_PATH.read_text() if CONTRACTS_PATH.exists() else ""


def _load_project_rules() -> str:
    """Concatenate all `.claude/rules/*.md` for project-augmented mode."""
    if not RULES_DIR.exists():
        return ""
    parts = []
    for rule in sorted(RULES_DIR.glob("*.md")):
        parts.append(f"# {rule.name}\n\n{rule.read_text()}")
    return "\n\n".join(parts)


def _build_system_prompt(config: str) -> str:
    base = PROMPT_PATH.read_text() if PROMPT_PATH.exists() else (
        "Summarize the document into Quick-tier markdown. Mirror the "
        "structure of CanonicalDoc.tier_summary + AnalysisReport.claims."
    )
    contracts = _load_contracts_md()
    parts = [base, "\n\n## Pipeline contracts reference\n\n", contracts]
    if config == "project":
        rules = _load_project_rules()
        if rules:
            parts.extend(["\n\n## Project rules\n\n", rules])
    return "".join(parts)


def _make_real_client() -> Any:
    """Lazy-import the Anthropic SDK; only called when no stub client is supplied."""
    import anthropic  # type: ignore[import-not-found]
    return anthropic.Anthropic()


def _compute_cost(usage: Any) -> float:
    in_tok = getattr(usage, "input_tokens", 0)
    out_tok = getattr(usage, "output_tokens", 0)
    return (
        in_tok / 1_000_000 * PRICE_PER_MTOK_INPUT
        + out_tok / 1_000_000 * PRICE_PER_MTOK_OUTPUT
    )


def run_oneshot(
    *,
    sample_path: Path,
    config: str,
    output_dir: Path,
    model: str = MODEL_DEFAULT,
    client: Any | None = None,
) -> dict[str, Any]:
    """Run a single Claude call over ``sample_path``; write summary + meta."""
    if config not in {"vanilla", "project"}:
        raise ValueError(f"config must be 'vanilla' or 'project', got {config!r}")

    sha = _sha256(sample_path)
    variant = f"anthropic-{config}"
    variant_dir = output_dir / sha / "external" / variant
    variant_dir.mkdir(parents=True, exist_ok=True)

    system = _build_system_prompt(config)
    user = sample_path.read_text(errors="replace")

    if client is None:
        client = _make_real_client()

    t0 = perf_counter()
    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    wall = perf_counter() - t0

    summary = response.content[0].text
    usage = getattr(response, "usage", None)

    summary_path = variant_dir / "summary.md"
    summary_path.write_text(summary)

    meta = {
        "variant": variant,
        "transport": "anthropic_sdk",
        "config": config,
        "model": getattr(response, "model", model),
        "wall_seconds": round(wall, 3),
        "cost_usd": round(_compute_cost(usage), 6) if usage else 0.0,
        "input_tokens": getattr(usage, "input_tokens", 0) if usage else 0,
        "output_tokens": getattr(usage, "output_tokens", 0) if usage else 0,
        "cache_read_tokens": getattr(usage, "cache_read_input_tokens", 0) if usage else 0,
    }
    (variant_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")

    return {"variant": variant, "sample_sha256": sha, "summary_path": str(summary_path)}


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Anthropic SDK one-shot summarizer (external evaluator)."
    )
    parser.add_argument("sample", type=Path, help="Path to a single sample file")
    parser.add_argument(
        "--config", choices=["vanilla", "project"], default="vanilla",
        help="vanilla = no project context; project = +.claude/rules/",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("outputs"),
        help="Parent dir for outputs/<sha>/external/<variant>/",
    )
    parser.add_argument("--model", default=MODEL_DEFAULT)
    args = parser.parse_args(argv)
    result = run_oneshot(
        sample_path=args.sample,
        config=args.config,
        output_dir=args.output_dir,
        model=args.model,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
