# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Discover stage: filesystem walk → DiscoveryManifest.

Walks ``root`` with the given glob, computes sha256 per file, and emits a
DiscoveryManifest dict ready for gate validation.
"""
from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

CONTRACT_VERSION = "0.1.0"
_HASH_CHUNK = 65536


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(_HASH_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def discover(root: Path, glob: str = "**/*") -> dict[str, Any]:
    """Walk ``root`` matching ``glob``, return a DiscoveryManifest dict."""
    files: list[dict[str, Any]] = []
    for path in sorted(root.glob(glob)):
        if not path.is_file():
            continue
        files.append(
            {
                "path": str(path.relative_to(root)),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "file_type": path.suffix.lstrip(".").lower() or "bin",
            }
        )
    return {
        "version": CONTRACT_VERSION,
        "source": {"root": str(root), "kind": "folder"},
        "discovered_at": datetime.now(UTC).isoformat(),
        "files": files,
    }
