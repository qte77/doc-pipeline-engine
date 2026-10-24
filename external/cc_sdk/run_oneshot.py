#!/usr/bin/env python3
# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""External Claude Agent SDK (cc-sdk) one-shot summarizer.

Runs one ``claude_agent_sdk.query`` per sample. The system prompt is
`external/PROMPT.md` plus a by-path reference to `docs/contracts.md`
(CC variants read it on demand, like `external/cc_cli/run_headless.sh`).

- ``--config vanilla``: cwd is an empty temp dir and no setting sources are
  loaded, so no CLAUDE.md / `.claude/` context reaches the agent.
- ``--config project``: cwd is the repo root with the ``project`` setting
  source, so CLAUDE.md and `.claude/` are autoloaded.

Output: ``outputs/<sha>/external/cc-sdk-{vanilla,project}/{summary.md,meta.json}``.
Non-interactive SDK calls are metered usage, not subscription-covered.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from time import perf_counter
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROMPT_PATH = REPO_ROOT / "external" / "PROMPT.md"
CONTRACTS_PATH = REPO_ROOT / "docs" / "contracts.md"

MODEL_DEFAULT = "claude-opus-4-7"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _build_system_prompt() -> str:
    base = PROMPT_PATH.read_text() if PROMPT_PATH.exists() else (
        "Summarize the document into Quick-tier markdown. Mirror the "
        "structure of CanonicalDoc.tier_summary + AnalysisReport.claims."
    )
    return f"{base}\n\nPipeline contracts reference: {CONTRACTS_PATH}"


def _make_real_query() -> Any:
    """Lazy-import the Agent SDK; only called when no stub query is supplied."""
    from claude_agent_sdk import (  # type: ignore[import-not-found]
        ClaudeAgentOptions,
        query,
    )

    def _query(*, prompt: str, options: dict[str, Any]) -> Any:
        return query(prompt=prompt, options=ClaudeAgentOptions(**options))

    return _query


async def _collect_result(query_fn: Any, prompt: str, options: dict[str, Any]) -> Any:
    """Drain the message stream and return the final ResultMessage."""
    result = None
    async for message in query_fn(prompt=prompt, options=options):
        if hasattr(message, "total_cost_usd"):
            result = message
    if result is None:
        raise RuntimeError("claude_agent_sdk.query yielded no ResultMessage")
    return result


def _run_query(query_fn: Any, prompt: str, config: str, model: str) -> tuple[Any, float]:
    with tempfile.TemporaryDirectory(prefix="cc-sdk-vanilla-") as empty_cwd:
        options: dict[str, Any] = {
            "system_prompt": _build_system_prompt(),
            "model": model,
            "cwd": str(REPO_ROOT) if config == "project" else empty_cwd,
            "setting_sources": ["project"] if config == "project" else [],
        }
        t0 = perf_counter()
        result = asyncio.run(_collect_result(query_fn, prompt, options))
        return result, perf_counter() - t0


def run_oneshot(
    *,
    sample_path: Path,
    config: str,
    output_dir: Path,
    model: str = MODEL_DEFAULT,
    query_fn: Any | None = None,
) -> dict[str, Any]:
    """Run a single Agent SDK query over ``sample_path``; write summary + meta."""
    if config not in {"vanilla", "project"}:
        raise ValueError(f"config must be 'vanilla' or 'project', got {config!r}")

    sha = _sha256(sample_path)
    variant = f"cc-sdk-{config}"
    variant_dir = output_dir / sha / "external" / variant
    variant_dir.mkdir(parents=True, exist_ok=True)

    if query_fn is None:
        query_fn = _make_real_query()

    prompt = sample_path.read_text(errors="replace")
    result, wall = _run_query(query_fn, prompt, config, model)

    summary_path = variant_dir / "summary.md"
    summary_path.write_text(getattr(result, "result", None) or "")

    usage = getattr(result, "usage", None) or {}
    meta = {
        "variant": variant,
        "transport": "cc-sdk",
        "config": config,
        "model": getattr(result, "model", None) or model,
        "wall_seconds": round(wall, 3),
        "cost_usd": round(getattr(result, "total_cost_usd", None) or 0.0, 6),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
    }
    (variant_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")

    return {"variant": variant, "sample_sha256": sha, "summary_path": str(summary_path)}


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Claude Agent SDK one-shot summarizer (external evaluator)."
    )
    parser.add_argument("sample", type=Path, help="Path to a single sample file")
    parser.add_argument(
        "--config", choices=["vanilla", "project"], default="vanilla",
        help="vanilla = empty cwd, no settings; project = repo cwd, .claude/ autoloaded",
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
