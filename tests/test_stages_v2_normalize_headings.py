# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V2 normalize heading-tree reconstruction tests.

Covers the three heading patterns observed across the locked prototype
samples (formal-prefix legal headings, numbered with space, numbered
glued) plus the two fallbacks (zero headings, density cap exceeded).
"""
from __future__ import annotations

from doc_pipeline_engine.base.contracts import is_valid
from doc_pipeline_engine.stages.v2_normalize import normalize_v2

SHA = "0" * 64


def _bundle(text: str) -> dict:
    return {
        "version": "0.1.0",
        "source_path": "a.pdf",
        "source_sha256": SHA,
        "adapter": {"name": "kreuzberg", "version": "0.0.0"},
        "extracted_at": "2026-04-26T00:00:00+00:00",
        "content": {"text": text, "layout": []},
    }


def test_numbered_with_space_splits_into_sections_with_levels() -> None:
    text = (
        "1 Features\n"
        "Timer features description.\n"
        "2 Applications\n"
        "Application notes here.\n"
        "5.1 Specs\n"
        "Spec body text.\n"
    )

    canonical = normalize_v2(_bundle(text))
    children = canonical["root"]["children"]

    assert is_valid("CanonicalDoc", canonical)
    assert len(children) == 3
    assert [c["level"] for c in children] == [1, 1, 2]
    assert children[0]["title"] == "1 Features"
    assert children[1]["title"] == "2 Applications"
    assert children[2]["title"] == "5.1 Specs"
    assert children[0]["text"] == "Timer features description."


def test_formal_prefix_splits_into_level_one_sections() -> None:
    text = (
        "SECTION 1. SHORT TITLE.\n"
        "Body of section one.\n"
        "SEC. 2. FINDINGS.\n"
        "Findings body.\n"
        "SECTION 3. PURPOSE.\n"
        "Purpose body.\n"
    )

    canonical = normalize_v2(_bundle(text))
    children = canonical["root"]["children"]

    assert is_valid("CanonicalDoc", canonical)
    assert len(children) == 3
    assert all(c["level"] == 1 for c in children)
    assert children[0]["title"] == "SECTION 1. SHORT TITLE."
    assert children[1]["title"] == "SEC. 2. FINDINGS."


def test_numbered_glued_splits_into_sections() -> None:
    text = (
        "1Definitions used in the Contract\n"
        "Definitions body text follows.\n"
        "2Understanding the Contract\n"
        "Understanding body text follows.\n"
    )

    canonical = normalize_v2(_bundle(text))
    children = canonical["root"]["children"]

    assert is_valid("CanonicalDoc", canonical)
    assert len(children) == 2
    assert [c["level"] for c in children] == [1, 1]
    assert children[0]["title"].startswith("1Definitions")


def test_density_cap_falls_back_to_single_leaf() -> None:
    # Every line is heading-like → density 100% > 50% cap; falls back.
    text = "\n".join(f"{i} Heading {i}" for i in range(1, 11))

    canonical = normalize_v2(_bundle(text))
    children = canonical["root"]["children"]

    assert is_valid("CanonicalDoc", canonical)
    assert len(children) == 1
    assert children[0]["text"] == text
    assert "title" not in children[0]


def test_zero_headings_falls_back_to_single_leaf() -> None:
    text = "Just a long paragraph with no heading-like lines anywhere."

    canonical = normalize_v2(_bundle(text))
    children = canonical["root"]["children"]

    assert is_valid("CanonicalDoc", canonical)
    assert len(children) == 1
    assert children[0]["text"] == text
