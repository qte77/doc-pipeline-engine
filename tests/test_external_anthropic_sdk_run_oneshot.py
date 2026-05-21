# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Tests for the external Anthropic SDK one-shot summarizer.

External evaluator (not a pipeline stage). Reads a sample's raw
bytes (off-the-shelf realism, see ADR-0004), sends a single Claude
call, writes summary.md + meta.json to outputs/<sha>/external/<variant>/.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "_run_oneshot",
    REPO_ROOT / "external" / "anthropic_sdk" / "run_oneshot.py",
)
assert _spec and _spec.loader
_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_run)


def _stub_anthropic_client(text: str = "# Stub\n\nSummary line.\n") -> object:
    """Build a SimpleNamespace mimicking anthropic.Anthropic()'s call surface."""
    captured: dict[str, object] = {"system": None, "user": None}

    def _create(**kwargs: object) -> object:
        captured["system"] = kwargs.get("system")
        captured["user"] = (kwargs.get("messages") or [{}])[0].get("content")
        return SimpleNamespace(
            content=[SimpleNamespace(text=text)],
            usage=SimpleNamespace(
                input_tokens=100,
                output_tokens=50,
                cache_creation_input_tokens=0,
                cache_read_input_tokens=0,
            ),
            model="claude-opus-4-7",
        )

    return SimpleNamespace(
        messages=SimpleNamespace(create=_create),
        _captured=captured,
    )


def _write_sample(tmp_path: Path, content: str = "Sample document body.") -> Path:
    sample = tmp_path / "sample.txt"
    sample.write_text(content)
    return sample


def test_anthropic_oneshot_writes_summary_and_meta_to_variant_dir(
    tmp_path: Path,
) -> None:
    sample = _write_sample(tmp_path)
    out = tmp_path / "outputs"
    client = _stub_anthropic_client()

    result = _run.run_oneshot(
        sample_path=sample,
        config="vanilla",
        output_dir=out,
        client=client,
    )

    assert result["variant"] == "anthropic-vanilla"
    summary_path = out / result["sample_sha256"] / "external" / "anthropic-vanilla" / "summary.md"
    meta_path = summary_path.with_name("meta.json")
    assert summary_path.exists()
    assert meta_path.exists()

    meta = json.loads(meta_path.read_text())
    assert meta["variant"] == "anthropic-vanilla"
    assert meta["transport"] == "anthropic_sdk"
    assert meta["config"] == "vanilla"
    assert meta["input_tokens"] == 100
    assert meta["output_tokens"] == 50
    assert meta["cost_usd"] >= 0.0


def test_anthropic_oneshot_project_loads_claude_rules_into_system_prompt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sample = _write_sample(tmp_path)
    out = tmp_path / "outputs"

    # Fake .claude/rules/ at a known location, point the loader at it.
    rules_dir = tmp_path / ".claude" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "core-principles.md").write_text(
        "# Core principles\n\nKISS over clever.\n"
    )

    monkeypatch.setattr(_run, "RULES_DIR", rules_dir)

    client = _stub_anthropic_client()
    _run.run_oneshot(
        sample_path=sample,
        config="project",
        output_dir=out,
        client=client,
    )

    system_prompt = client._captured["system"]  # type: ignore[attr-defined]
    assert "KISS over clever." in system_prompt, (
        "project mode must hand-load .claude/rules/*.md into the system prompt"
    )


def test_anthropic_oneshot_inlines_contracts_md_into_system_prompt_with_fixme(
    tmp_path: Path,
) -> None:
    sample = _write_sample(tmp_path)
    out = tmp_path / "outputs"
    client = _stub_anthropic_client()

    _run.run_oneshot(
        sample_path=sample,
        config="vanilla",
        output_dir=out,
        client=client,
    )

    system_prompt = client._captured["system"]  # type: ignore[attr-defined]
    # docs/contracts.md gets inlined for both vanilla and project modes —
    # external evaluators see the structural target.
    assert "## CanonicalDoc" in system_prompt
    assert "## AnalysisReport" in system_prompt

    # FIXME marker must be in the source code itself (workaround flag for
    # the SDK's lack of file-reading; see ADR-0004 mitigation note).
    source = (REPO_ROOT / "external" / "anthropic_sdk" / "run_oneshot.py").read_text()
    assert "FIXME(sdk-no-file-reading)" in source
