# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""ExtractionBundle model — uniform Adapter output."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from ._common import (
    CONTRACT_VERSION_LITERAL,
    Confidence,
    ContractVersion,
    Sha256Hex,
    StrictModel,
)


class AdapterInfo(StrictModel):
    """Identifies the extraction backend that produced the bundle."""

    name: str
    version: str


class LayoutBlock(StrictModel):
    """One layout block in reading order."""

    kind: Literal[
        "heading",
        "paragraph",
        "list",
        "caption",
        "table",
        "figure",
        "code",
        "formula",
        "footnote",
    ]
    page: int = Field(ge=1)
    bbox: list[float] = Field(
        min_length=4,
        max_length=4,
        description="[x0, y0, x1, y1] in page units",
    )
    level: int | None = Field(
        default=None,
        description="Heading level 1..6 (if kind=heading)",
    )
    text: str


class Table(StrictModel):
    """Tabular content extracted on a single page."""

    page: int = Field(ge=1)
    caption: str | None = None
    rows: list[list[str]] | None = None


class Figure(StrictModel):
    """Figure or image reference on a single page."""

    page: int = Field(ge=1)
    caption: str | None = None
    image_path: str | None = Field(
        default=None,
        description="Path to extracted image relative to bundle",
    )


class Content(StrictModel):
    """Container for text + layout + supplemental tables/figures/metadata."""

    text: str = Field(description="Plain-text concatenation of all text blocks")
    layout: list[LayoutBlock] = Field(description="Flat list of layout blocks in reading order")
    tables: list[Table] | None = None
    figures: list[Figure] | None = None
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Docinfo: title, author, creation date, producer, keywords, etc.",
    )


class ExtractionBundle(StrictModel):
    """Uniform output schema every Adapter must emit. Contains text, layout tree, tables, figures, images."""

    version: ContractVersion = CONTRACT_VERSION_LITERAL
    source_path: str
    source_sha256: Sha256Hex
    adapter: AdapterInfo
    extracted_at: str
    confidence: Confidence | None = Field(
        default=None,
        description="Adapter self-reported confidence; gate G_extract rejects < pack threshold (default 0.7)",
    )
    content: Content
    warnings: list[str] | None = None
