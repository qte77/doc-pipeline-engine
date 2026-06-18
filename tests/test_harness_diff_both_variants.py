# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Diff harness tests with both legs mocked.

Real V1 calls Anthropic; real V2 needs render extras. We mock both via
monkeypatch and assert the harness's own behaviour: shape of DiffReport,
artifact write-out, axes computation, JSON serialisation.
"""
from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import pytest

pytest.importorskip("docx")
pytest.importorskip("markdown")
pytest.importorskip("weasyprint")

from doc_pipeline_engine.harness import (
    DiffReport,
    LegResult,
    _to_json,
    run_both,
)
from doc_pipeline_engine.render.formats import RenderArtifacts
from doc_pipeline_engine.stages import extract as extract_module

SHA = "0" * 64


def _stub_extract_file_sync(_path: str, **_kwargs: object) -> object:
    class R:
        content = "Hello world. Some body."
        metadata: ClassVar[dict] = {}
        tables: ClassVar[list] = []
    return R()


@pytest.fixture
def fake_kreuzberg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extract_module, "_extract_file_sync", _stub_extract_file_sync)
    monkeypatch.setattr(extract_module, "_kreuzberg_version", "stub")


@pytest.fixture
def fake_anthropic_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace V1 stage functions with deterministic stubs."""
    valid_canonical = {
        "version": "0.1.0",
        "source_sha256": SHA,
        "built_at": "2026-04-26T00:00:00+00:00",
        "root": {"id": "s.0", "level": 0, "kind": "doc", "text": ""},
        "tier_summary": {"l0": "summary", "l1": "longer summary"},
    }
    valid_report = {
        "version": "0.1.0",
        "source_sha256": SHA,
        "analyzed_at": "2026-04-26T00:00:00+00:00",
        "claims": [{"id": "c1", "text": "x is y", "node_refs": ["s.0"]}],
        "entities": [],
    }
    valid_eval = {
        "version": "0.1.0",
        "evaluated_at": "2026-04-26T00:00:00+00:00",
        "tier": "quick",
        "verdict": "pass",
        "scores": {"schema_valid": {"value": 1.0, "threshold": 1.0, "passed": True}},
    }
    artifacts = RenderArtifacts(md="# v1 md", docx=b"PK\x03\x04", pdf=b"%PDF-stub")

    monkeypatch.setattr(
        "doc_pipeline_engine.stages.anthropic_sdk_normalize.normalize_anthropic_sdk",
        lambda bundle, **_: valid_canonical,
    )
    monkeypatch.setattr(
        "doc_pipeline_engine.stages.anthropic_sdk_analyze.analyze_anthropic_sdk",
        lambda canonical, **_: valid_report,
    )
    monkeypatch.setattr(
        "doc_pipeline_engine.stages.anthropic_sdk_render.render_anthropic_sdk",
        lambda report, **_: artifacts,
    )
    monkeypatch.setattr(
        "doc_pipeline_engine.stages.anthropic_sdk_eval.eval_anthropic_sdk",
        lambda *args, **_: valid_eval,
    )


def _write_sample(tmp_path: Path) -> Path:
    p = tmp_path / "a.pdf"
    p.write_bytes(b"hello pdf")
    return p


def test_harness_run_both_returns_diff_report(
    tmp_path: Path, fake_kreuzberg: None, fake_anthropic_sdk: None
) -> None:
    sample = _write_sample(tmp_path)

    report = run_both(sample)

    assert isinstance(report, DiffReport)
    assert report.sample_sha256 != ""
    assert isinstance(report.anthropic_sdk, LegResult)
    assert isinstance(report.local, LegResult)


def test_harness_anthropic_sdk_and_local_legs_each_emit_three_post_extraction_contracts(
    tmp_path: Path, fake_kreuzberg: None, fake_anthropic_sdk: None
) -> None:
    sample = _write_sample(tmp_path)

    report = run_both(sample)

    # post-extraction contracts: canonical, analysis, eval
    assert len(report.anthropic_sdk.contracts) == 3
    assert len(report.local.contracts) == 3


def test_harness_extraction_bundle_is_shared_between_legs(
    tmp_path: Path, fake_kreuzberg: None, fake_anthropic_sdk: None
) -> None:
    sample = _write_sample(tmp_path)

    report = run_both(sample)

    # Real extraction bundle from Kreuzberg (stubbed) — single source of truth.
    assert report.extraction_bundle["adapter"]["name"] == "kreuzberg"
    assert report.extraction_bundle["source_sha256"] == report.sample_sha256
    # V2 (deterministic) propagates sha256 from the bundle into its canonical doc.
    # V1 is stubbed here with a placeholder sha256, so we don't equality-check it
    # against the bundle — that's covered by the real-API integration test.
    assert report.local.contracts[0]["source_sha256"] == report.extraction_bundle["source_sha256"]


def test_harness_axes_includes_latency_ratio(
    tmp_path: Path, fake_kreuzberg: None, fake_anthropic_sdk: None
) -> None:
    sample = _write_sample(tmp_path)

    report = run_both(sample)

    assert "anthropic_sdk_total_seconds" in report.axes
    assert "local_total_seconds" in report.axes
    assert "latency_ratio_anthropic_sdk_over_local" in report.axes


def test_harness_writes_artifacts_to_output_dir_when_given(
    tmp_path: Path, fake_kreuzberg: None, fake_anthropic_sdk: None
) -> None:
    sample = _write_sample(tmp_path)
    out = tmp_path / "outputs"

    report = run_both(sample, output_dir=out)

    sha_dir = out / report.sample_sha256
    assert (sha_dir / "anthropic_sdk" / "summary.md").exists()
    assert (sha_dir / "anthropic_sdk" / "summary.docx").exists()
    assert (sha_dir / "anthropic_sdk" / "summary.pdf").exists()
    assert (sha_dir / "local" / "summary.md").exists()


def test_harness_to_json_omits_artifact_bytes(
    tmp_path: Path, fake_kreuzberg: None, fake_anthropic_sdk: None
) -> None:
    sample = _write_sample(tmp_path)
    report = run_both(sample)

    payload = _to_json(report)

    assert payload["anthropic_sdk"]["artifacts"]["md_chars"] > 0
    assert payload["anthropic_sdk"]["artifacts"]["docx_bytes"] > 0
    assert payload["anthropic_sdk"]["artifacts"]["pdf_bytes"] > 0
    # Bytes themselves are not in the JSON payload (would not be serialisable
    # cleanly and would bloat output).
    assert "docx" not in payload["anthropic_sdk"]["artifacts"]


def test_harness_run_both_raises_when_sample_missing(
    tmp_path: Path, fake_kreuzberg: None, fake_anthropic_sdk: None
) -> None:
    missing = tmp_path / "nope.pdf"

    with pytest.raises(FileNotFoundError):
        run_both(missing)
