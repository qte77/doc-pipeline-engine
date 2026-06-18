# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V2 normalize: ExtractionBundle → CanonicalDoc, deterministic.

Kreuzberg returns plain text without layout structure, so we reconstruct a
flat heading tree from heuristic detection over line prefixes (formal
``SECTION``/``SEC.``/``CHAPTER``/``ARTICLE``/``PART``, numbered
``5.1 Title``, glued numbered ``1Title``). Falls back to a single-leaf
section when no headings or implausibly many headings are detected.
tier_summary is a deterministic head-of-text excerpt — Quick (l0) takes
the first 200 chars, Comprehensive (l1) the first 1000.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from doc_pipeline_engine.models.canonical_doc import (
    CanonicalDoc,
    Node,
    TierSummary,
)
from doc_pipeline_engine.models.extraction_bundle import ExtractionBundle  # noqa: TC001

_L0_CHARS = 200
_L1_CHARS = 1000
_HEADING_MAX_LEN = 100
_DENSITY_CAP = 0.5
_MAX_LEVEL = 6

_FORMAL_PREFIX = re.compile(
    r"^\s*(?P<kw>SECTION|SEC\.|CHAPTER|ARTICLE|PART)\s+\S+",
)
_NUM_SPACED = re.compile(r"^\s*(?P<num>\d+(?:\.\d+)*)\s+\S")
_NUM_GLUED = re.compile(r"^\s*(?P<num>\d+(?:\.\d+)*)(?P<rest>[A-Z]\S{3,}.*)$")


def _truncate(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n].rstrip() + "…"


def _is_heading(line: str) -> tuple[bool, int, str]:
    """Return (is_heading, level, title). level 0 means not a heading."""
    stripped = line.strip()
    if not stripped or len(stripped) > _HEADING_MAX_LEN:
        return False, 0, ""
    m = _FORMAL_PREFIX.match(stripped)
    if m:
        return True, 1, stripped
    m = _NUM_SPACED.match(stripped)
    if m:
        level = min(m.group("num").count(".") + 1, _MAX_LEVEL)
        return True, level, stripped
    m = _NUM_GLUED.match(stripped)
    if m:
        level = min(m.group("num").count(".") + 1, _MAX_LEVEL)
        return True, level, stripped
    return False, 0, ""


def _split_into_sections(text: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    non_empty = sum(1 for ln in lines if ln.strip())
    headings: list[tuple[int, int, str]] = []  # (line_idx, level, title)
    for idx, ln in enumerate(lines):
        is_h, level, title = _is_heading(ln)
        if is_h:
            headings.append((idx, level, title))
    if not headings:
        return []
    if non_empty and len(headings) / non_empty > _DENSITY_CAP:
        return []
    sections: list[dict[str, Any]] = []
    for i, (line_idx, level, title) in enumerate(headings):
        end = headings[i + 1][0] if i + 1 < len(headings) else len(lines)
        body = "\n".join(lines[line_idx + 1 : end]).strip()
        sections.append({"level": level, "title": title, "text": body})
    return sections


def normalize_local(bundle: ExtractionBundle) -> CanonicalDoc:
    """ExtractionBundle → CanonicalDoc, deterministic."""
    text = bundle.content.text
    sections = _split_into_sections(text)
    if sections:
        children = [
            Node(
                id=f"s.{i + 1}",
                level=s["level"],
                kind="section",
                title=s["title"],
                text=s["text"],
            )
            for i, s in enumerate(sections)
        ]
    else:
        children = [Node(id="s.1", level=1, kind="section", text=text)]
    return CanonicalDoc(
        source_sha256=bundle.source_sha256,
        built_at=datetime.now(UTC).isoformat(),
        root=Node(id="s.0", level=0, kind="doc", text="", children=children),
        tier_summary=TierSummary(
            l0=_truncate(text, _L0_CHARS),
            l1=_truncate(text, _L1_CHARS),
        ),
    )
