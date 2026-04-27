# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""DiscoveryManifest model — Discover stage output."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._common import (
    CONTRACT_VERSION_LITERAL,
    ContractVersion,
    Sha256Hex,
    StrictModel,
)


class Source(StrictModel):
    """Ingest root that produced the file list."""

    root: str = Field(description="Absolute path to the ingest root")
    kind: Literal["folder", "url", "repo"]


class FileEntry(StrictModel):
    """One discovered file with hash and detected file-type."""

    path: str = Field(description="Path relative to source.root")
    size_bytes: int = Field(ge=0)
    sha256: Sha256Hex
    file_type: Literal["pdf", "docx", "xlsx", "txt", "md", "image", "unknown"]
    mime: str | None = None
    detected_at: str | None = None


class DiscoveryManifest(StrictModel):
    """Output of the Discover stage — enumerates source files with hash and detected file-type."""

    version: ContractVersion = CONTRACT_VERSION_LITERAL
    source: Source
    discovered_at: str
    files: list[FileEntry]
