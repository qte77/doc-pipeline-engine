# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V1 eval stage tests."""
from __future__ import annotations

import pytest

pytest.importorskip("docx")

from doc_pipeline_engine.base.contracts import is_valid  # noqa: E402
from doc_pipeline_engine.render.formats import RenderArtifacts  # noqa: E402
from doc_pipeline_engine.stages.v1_eval import eval_v1  # noqa: E402

SHA = "0" * 64


def _bundle() -> dict:
    return {
        "version": "0.1.0",
        "source_path": "a.pdf",
        "source_sha256": SHA,
        "adapter": {"name": "stub", "version": "0.0.0"},
        "extracted_at": "2026-04-26T00:00:00+00:00",
        "content": {"text": "hi", "layout": []},
    }


def _canonical() -> dict:
    return {
        "version": "0.1.0",
        "source_sha256": SHA,
        "built_at": "2026-04-26T00:00:00+00:00",
        "root": {"id": "s.0", "level": 0, "kind": "doc", "text": ""},
        "tier_summary": {"l0": "x", "l1": "y"},
    }


def _report() -> dict:
    return {
        "version": "0.1.0",
        "source_sha256": SHA,
        "analyzed_at": "2026-04-26T00:00:00+00:00",
        "claims": [{"id": "c1", "text": "x", "node_refs": ["s.0"]}],
        "entities": [],
    }


def test_stages_v1_eval_emits_valid_eval_report() -> None:
    art = RenderArtifacts(md="# x", docx=b"PK\x03\x04", pdf=b"%PDF-")

    report = eval_v1(_bundle(), _canonical(), _report(), art)

    assert is_valid("EvalReport", report)


def test_stages_v1_eval_records_pass_when_gates_passed() -> None:
    art = RenderArtifacts(md="# x", docx=b"PK\x03\x04", pdf=b"%PDF-")

    report = eval_v1(_bundle(), _canonical(), _report(), art)

    assert report["verdict"] == "pass"
    assert report["scores"]["schema_valid"]["passed"] is True
