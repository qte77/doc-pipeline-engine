# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Tests for the external Claude Agent SDK (cc-sdk) one-shot summarizer.

External evaluator (not a pipeline stage). A stub replaces
``claude_agent_sdk.query``: it captures the prompt + options and yields a
fixed ResultMessage-shaped object, so no SDK install or API key is needed.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "_cc_sdk_run_oneshot",
    REPO_ROOT / "external" / "cc_sdk" / "run_oneshot.py",
)
assert _spec
assert _spec.loader
_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_run)


def _stub_query(text: str = "# Stub\n\nSummary line.\n") -> Any:
    """Mimic claude_agent_sdk.query: async generator ending in a ResultMessage."""
    captured: dict[str, Any] = {}

    async def _query(*, prompt: str, options: dict[str, Any]) -> Any:
        captured["prompt"] = prompt
        captured["options"] = options
        cwd = Path(options["cwd"])
        captured["cwd_entries"] = sorted(p.name for p in cwd.iterdir())
        yield SimpleNamespace(
            result=text,
            total_cost_usd=0.0123,
            usage={"input_tokens": 100, "output_tokens": 50, "cache_read_input_tokens": 7},
            model="claude-opus-4-7",
        )

    _query.captured = captured  # type: ignore[attr-defined]
    return _query


def _write_sample(tmp_path: Path, content: str = "Sample document body.") -> Path:
    sample = tmp_path / "sample.txt"
    sample.write_text(content)
    return sample


def test_cc_sdk_oneshot_writes_summary_and_meta_to_variant_dir(tmp_path: Path) -> None:
    sample = _write_sample(tmp_path)
    out = tmp_path / "outputs"
    query = _stub_query()

    result = _run.run_oneshot(
        sample_path=sample, config="vanilla", output_dir=out, query_fn=query
    )

    assert result["variant"] == "cc-sdk-vanilla"
    summary_path = out / result["sample_sha256"] / "external" / "cc-sdk-vanilla" / "summary.md"
    assert summary_path.read_text() == "# Stub\n\nSummary line.\n"

    meta = json.loads(summary_path.with_name("meta.json").read_text())
    assert meta["variant"] == "cc-sdk-vanilla"
    assert meta["transport"] == "cc-sdk"
    assert meta["config"] == "vanilla"
    assert meta["cost_usd"] == 0.0123
    assert meta["input_tokens"] == 100
    assert meta["output_tokens"] == 50
    assert "Sample document body." in query.captured["prompt"]


def test_cc_sdk_oneshot_vanilla_uses_empty_cwd_for_no_project_context(tmp_path: Path) -> None:
    sample = _write_sample(tmp_path)
    query = _stub_query()

    _run.run_oneshot(
        sample_path=sample, config="vanilla", output_dir=tmp_path / "outputs", query_fn=query
    )

    options = query.captured["options"]
    assert Path(options["cwd"]).resolve() != REPO_ROOT
    assert query.captured["cwd_entries"] == [], "vanilla cwd must be empty (no CLAUDE.md/.claude)"
    assert options["setting_sources"] == []


def test_cc_sdk_oneshot_project_uses_repo_root_cwd_for_autoload(tmp_path: Path) -> None:
    sample = _write_sample(tmp_path)
    query = _stub_query()

    _run.run_oneshot(
        sample_path=sample, config="project", output_dir=tmp_path / "outputs", query_fn=query
    )

    options = query.captured["options"]
    assert Path(options["cwd"]).resolve() == REPO_ROOT
    assert "project" in options["setting_sources"]
    # CC variants reference contracts.md by path rather than inlining it.
    assert str(_run.CONTRACTS_PATH) in options["system_prompt"]
