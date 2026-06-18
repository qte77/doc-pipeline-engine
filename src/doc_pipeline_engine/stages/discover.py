# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Discover stage: filesystem walk → DiscoveryManifest."""
from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from doc_pipeline_engine.models.discovery_manifest import (
    DiscoveryManifest,
    FileEntry,
    Source,
)

if TYPE_CHECKING:
    from pathlib import Path

_HASH_CHUNK = 65536

_EXT_MAP: dict[str, str] = {
    "pdf": "pdf",
    "docx": "docx",
    "xlsx": "xlsx",
    "txt": "txt",
    "md": "md",
    "png": "image",
    "jpg": "image",
    "jpeg": "image",
    "tiff": "image",
    "bmp": "image",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(_HASH_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def discover(root: Path, glob: str = "**/*") -> DiscoveryManifest:
    """Walk ``root`` matching ``glob``, return a DiscoveryManifest."""
    files: list[FileEntry] = []
    for path in sorted(root.glob(glob)):
        if not path.is_file():
            continue
        ext = path.suffix.lstrip(".").lower()
        files.append(
            FileEntry(
                path=str(path.relative_to(root)),
                size_bytes=path.stat().st_size,
                sha256=_sha256(path),
                file_type=_EXT_MAP.get(ext, "unknown"),
            )
        )
    return DiscoveryManifest(
        source=Source(root=str(root), kind="folder"),
        discovered_at=datetime.now(UTC).isoformat(),
        files=files,
    )
