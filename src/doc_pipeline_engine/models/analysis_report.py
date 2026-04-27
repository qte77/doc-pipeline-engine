# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""AnalysisReport model — Analyze stage output (claims, entities, relations, citations)."""
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


class AnalyzerInfo(StrictModel):
    """Identifies the analyzer that produced the report."""

    name: str
    version: str
    model: str | None = None


class Claim(StrictModel):
    """One assertion extracted from the document."""

    id: str
    text: str
    kind: (
        Literal["factual", "normative", "definitional", "measurement", "recommendation"] | None
    ) = None
    node_refs: list[str] = Field(
        min_length=1,
        description="CanonicalDoc node ids supporting this claim",
    )
    confidence: Confidence | None = None


class Entity(StrictModel):
    """A named entity surfaced in the document."""

    id: str
    name: str
    kind: Literal[
        "person",
        "org",
        "product",
        "standard",
        "measurement",
        "location",
        "concept",
        "other",
    ]
    aliases: list[str] | None = None


class Relation(StrictModel):
    """Subject–predicate–object triple grounded in the document."""

    subject: str
    predicate: str
    object: str
    evidence_node_refs: list[str] | None = None


class Citation(StrictModel):
    """Bibliographic reference cited by one or more claims."""

    id: str
    raw: str
    doi: str | None = None
    url: str | None = None
    cited_by_claim_ids: list[str] | None = None


class AnalysisReport(StrictModel):
    """Analyze stage output — claims, entities, relations, citations extracted from CanonicalDoc."""

    version: ContractVersion = CONTRACT_VERSION_LITERAL
    source_sha256: Sha256Hex
    analyzed_at: str
    analyzer: AnalyzerInfo | None = None
    claims: list[Claim] = Field(min_length=1)
    entities: list[Entity]
    relations: list[Relation] | None = None
    citations: list[Citation] | None = None
    missing_required_fields: list[str] | None = Field(
        default=None,
        description="Populated when InputFormat declares required fields that are absent",
    )
