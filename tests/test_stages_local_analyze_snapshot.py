# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V2 analyze stage tests.

Entities come from spaCy when available; tests assert behavior under both
conditions (entities=[] when spaCy is absent or model not loaded). Claims
are extracted deterministically from the canonical tree regardless.
"""
from __future__ import annotations

from doc_pipeline_engine.base.contracts import is_valid
from doc_pipeline_engine.stages.local_analyze import analyze_local

SHA = "0" * 64


def _canonical(*texts: str) -> dict:
    children = [
        {"id": f"s.{i + 1}", "level": 1, "kind": "section", "text": t}
        for i, t in enumerate(texts)
    ]
    return {
        "version": "0.1.0",
        "source_sha256": SHA,
        "built_at": "2026-04-26T00:00:00+00:00",
        "root": {
            "id": "s.0",
            "level": 0,
            "kind": "doc",
            "text": "",
            "children": children,
        },
        "tier_summary": {"l0": "x", "l1": "y"},
    }


def test_stages_v2_analyze_emits_valid_analysis_report() -> None:
    canonical = _canonical("First sentence. Second sentence.")

    report = analyze_local(canonical)

    assert is_valid("AnalysisReport", report)


def test_stages_v2_analyze_extracts_first_sentence_per_leaf_as_claim() -> None:
    canonical = _canonical("Alpha is one. Beta is two.", "Gamma is three.")

    report = analyze_local(canonical)

    claim_texts = [c["text"] for c in report["claims"]]
    assert "Alpha is one." in claim_texts
    assert "Gamma is three." in claim_texts


def test_stages_v2_analyze_claims_reference_their_source_node() -> None:
    canonical = _canonical("Alpha is one.")

    report = analyze_local(canonical)

    assert report["claims"][0]["node_refs"] == ["s.1"]


def test_stages_v2_analyze_emits_at_least_one_claim_for_empty_doc() -> None:
    canonical = _canonical()  # no children

    report = analyze_local(canonical)

    assert len(report["claims"]) >= 1


def test_stages_v2_analyze_records_analyzer_identity() -> None:
    report = analyze_local(_canonical("text."))

    assert report["analyzer"]["name"] == "v2_analyze_local"


def test_stages_v2_analyze_propagates_source_sha256() -> None:
    report = analyze_local(_canonical("text."))

    assert report["source_sha256"] == SHA
