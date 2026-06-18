# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Discover stage: walks a root directory, computes sha256 per file, emits
a valid DiscoveryManifest dict.
"""
from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from doc_pipeline_engine.base.contracts import is_valid
from doc_pipeline_engine.stages.discover import discover

if TYPE_CHECKING:
    from pathlib import Path


def _write(p: Path, content: bytes) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)


def test_stages_discover_emits_valid_discovery_manifest(tmp_path: Path) -> None:
    _write(tmp_path / "a.pdf", b"hello pdf")
    _write(tmp_path / "sub" / "b.docx", b"hello docx")

    manifest = discover(tmp_path)

    assert is_valid("DiscoveryManifest", manifest)


def test_stages_discover_lists_files_with_sha256_and_size(tmp_path: Path) -> None:
    payload = b"hello pdf"
    _write(tmp_path / "a.pdf", payload)

    manifest = discover(tmp_path)

    files = {f["path"]: f for f in manifest["files"]}
    assert "a.pdf" in files
    assert files["a.pdf"]["size_bytes"] == len(payload)
    assert files["a.pdf"]["sha256"] == hashlib.sha256(payload).hexdigest()
    assert files["a.pdf"]["file_type"] == "pdf"


def test_stages_discover_respects_glob_filter(tmp_path: Path) -> None:
    _write(tmp_path / "a.pdf", b"x")
    _write(tmp_path / "b.txt", b"x")

    manifest = discover(tmp_path, glob="**/*.pdf")

    paths = {f["path"] for f in manifest["files"]}
    assert paths == {"a.pdf"}


def test_stages_discover_source_records_root_and_kind(tmp_path: Path) -> None:
    _write(tmp_path / "a.pdf", b"x")

    manifest = discover(tmp_path)

    assert manifest["source"]["root"] == str(tmp_path)
    assert manifest["source"]["kind"] == "folder"
