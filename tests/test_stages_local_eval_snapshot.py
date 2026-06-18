# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V2 eval stage tests."""
from __future__ import annotations

import pytest

pytest.importorskip("docx")

from doc_pipeline_engine.base.contracts import is_valid
from doc_pipeline_engine.render.formats import RenderArtifacts
from doc_pipeline_engine.stages.local_eval import eval_local

SHA = "0" * 64


def test_stages_v2_eval_emits_valid_eval_report() -> None:
    art = RenderArtifacts(md="# x", docx=b"PK\x03\x04", pdf=b"%PDF-")

    report = eval_local({}, {}, {}, art)

    assert is_valid("EvalReport", report)


def test_stages_v2_eval_records_pass_when_gates_passed() -> None:
    art = RenderArtifacts(md="# x", docx=b"PK\x03\x04", pdf=b"%PDF-")

    report = eval_local({}, {}, {}, art)

    assert report["verdict"] == "pass"
