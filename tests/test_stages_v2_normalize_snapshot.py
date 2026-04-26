# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V2 normalize stage tests — pure stdlib, fully deterministic."""
from __future__ import annotations

from doc_pipeline_engine.base.contracts import is_valid
from doc_pipeline_engine.stages.v2_normalize import normalize_v2

SHA = "0" * 64


def _bundle(text: str = "Hello world.") -> dict:
    return {
        "version": "0.1.0",
        "source_path": "a.pdf",
        "source_sha256": SHA,
        "adapter": {"name": "kreuzberg", "version": "0.0.0"},
        "extracted_at": "2026-04-26T00:00:00+00:00",
        "content": {"text": text, "layout": []},
    }


def test_stages_v2_normalize_emits_valid_canonical_doc() -> None:
    canonical = normalize_v2(_bundle())

    assert is_valid("CanonicalDoc", canonical)


def test_stages_v2_normalize_propagates_source_sha256() -> None:
    canonical = normalize_v2(_bundle())

    assert canonical["source_sha256"] == SHA


def test_stages_v2_normalize_root_carries_extracted_text_in_first_section() -> None:
    text = "Some extracted text."

    canonical = normalize_v2(_bundle(text))

    assert canonical["root"]["children"][0]["text"] == text


def test_stages_v2_normalize_tier_summary_truncates_at_200_and_1000_chars() -> None:
    long_text = "abc " * 400  # 1600 chars

    canonical = normalize_v2(_bundle(long_text))

    assert len(canonical["tier_summary"]["l0"]) <= 201  # 200 + ellipsis
    assert len(canonical["tier_summary"]["l1"]) <= 1001
    assert canonical["tier_summary"]["l0"].endswith("…")
