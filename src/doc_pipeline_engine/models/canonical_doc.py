# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""CanonicalDoc model — normalized L0/L1/L2 content tree."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._common import (
    CONTRACT_VERSION_LITERAL,
    Confidence,
    ContractVersion,
    Sha256Hex,
    StrictModel,
)


class SourceRef(StrictModel):
    """Back-pointer from a Node to one ExtractionBundle.content.layout entry."""

    layout_index: int = Field(ge=0)
    page: int = Field(ge=1)


class Node(StrictModel):
    """One tree node — section, paragraph, table, etc.

    The tree is recursive via ``children``. Levels run 0..6 (0=doc,
    1=section, 2=subsection, 3+=deeper).
    """

    id: str = Field(description="Stable node id (e.g. 's.1.2.3')")
    level: int = Field(ge=0, le=6, description="0=doc, 1=section, 2=subsection, 3+=deeper")
    kind: Literal[
        "doc",
        "section",
        "subsection",
        "paragraph",
        "list",
        "table",
        "figure",
        "caption",
        "code",
        "formula",
        "footnote",
    ]
    title: str | None = None
    text: str
    source_refs: list[SourceRef] | None = Field(
        default=None,
        description="Back-pointers to ExtractionBundle.content.layout entries",
    )
    children: list[Node] | None = None


class InputFormatRef(StrictModel):
    """If RecognizeInputFormat matched, which format was used to guide normalization."""

    id: str | None = None
    version: str | None = None
    confidence: Confidence | None = None


class TierSummary(StrictModel):
    """OpenViking-style tiered view: L0 summary + L1 summary; L2 is the full content."""

    l0: str = Field(description="≤100 tokens — title + one-line gist")
    l1: str = Field(description="≤2000 tokens — section-level summary")


class CanonicalDoc(StrictModel):
    """Normalized L0/L1/L2 content tree — the single most load-bearing contract.

    Feeds RAG, analysis, and the future doc-graph.
    """

    version: ContractVersion = CONTRACT_VERSION_LITERAL
    source_sha256: Sha256Hex
    built_at: str
    input_format: InputFormatRef | None = None
    root: Node
    tier_summary: TierSummary
