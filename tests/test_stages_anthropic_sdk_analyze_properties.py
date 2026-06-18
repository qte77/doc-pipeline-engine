# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V1 analyze stage tests with stubbed Anthropic client."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from types import SimpleNamespace

from doc_pipeline_engine.models.analysis_report import AnalysisReport
from doc_pipeline_engine.models.canonical_doc import CanonicalDoc, Node, TierSummary
from doc_pipeline_engine.stages.anthropic_sdk_analyze import analyze_anthropic_sdk

SHA = "0" * 64

_VALID_PAYLOAD = {
    "claims": [
        {"id": "c1", "text": "x is y", "node_refs": ["s.1"], "kind": "factual"}
    ],
    "entities": [
        {"id": "e1", "name": "Acme", "kind": "org"}
    ],
}


def _stub_client(response_text: str) -> object:
    def _create(**_kwargs: object) -> object:
        return SimpleNamespace(content=[SimpleNamespace(text=response_text)])

    return SimpleNamespace(messages=SimpleNamespace(create=_create))


def _canonical() -> CanonicalDoc:
    return CanonicalDoc(
        source_sha256=SHA,
        built_at=datetime.now(UTC).isoformat(),
        root=Node(
            id="s.0",
            level=0,
            kind="doc",
            text="",
            children=[Node(id="s.1", level=1, kind="section", title="T", text="b")],
        ),
        tier_summary=TierSummary(l0="summary", l1="long summary"),
    )


def test_stages_v1_analyze_returns_analysis_report_instance() -> None:
    client = _stub_client(json.dumps(_VALID_PAYLOAD))

    report = analyze_anthropic_sdk(_canonical(), client=client)

    assert isinstance(report, AnalysisReport)


def test_stages_v1_analyze_records_analyzer_identity() -> None:
    client = _stub_client(json.dumps(_VALID_PAYLOAD))

    report = analyze_anthropic_sdk(_canonical(), client=client, model="stub-model")

    assert report.analyzer.name == "v1_analyze_claude"
    assert report.analyzer.model == "stub-model"


def test_stages_v1_analyze_propagates_source_sha256() -> None:
    client = _stub_client(json.dumps(_VALID_PAYLOAD))

    report = analyze_anthropic_sdk(_canonical(), client=client)

    assert report.source_sha256 == SHA
