# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Extract stage: Kreuzberg-backed adapter that consumes a DiscoveryManifest
file entry and emits an ExtractionBundle.

Unit tests stub Kreuzberg via monkeypatch so they run without the optional
``extract`` dep installed. Real-Kreuzberg integration is exercised by tests
marked ``integration`` (skipped in CI).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from doc_pipeline_engine.base.contracts import is_valid
from doc_pipeline_engine.stages import extract as extract_module
from doc_pipeline_engine.stages.extract import extract


@dataclass
class _StubResult:
    content: str = ""
    metadata: dict[str, Any] | None = None
    tables: list[Any] | None = None


def _stub_extract_file_sync(_path: str, **_kwargs: Any) -> _StubResult:
    return _StubResult(content="hello world", metadata={}, tables=[])


@pytest.fixture
def fake_kreuzberg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extract_module, "_extract_file_sync", _stub_extract_file_sync)
    monkeypatch.setattr(extract_module, "_kreuzberg_version", "stub")


def _write_pdf(tmp_path: Path, name: str = "a.pdf") -> tuple[Path, dict[str, Any]]:
    payload = b"hello pdf"
    p = tmp_path / name
    p.write_bytes(payload)
    file_entry = {
        "path": name,
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "file_type": "pdf",
    }
    return p, file_entry


def test_stages_extract_emits_valid_extraction_bundle(
    tmp_path: Path, fake_kreuzberg: None
) -> None:
    _, entry = _write_pdf(tmp_path)

    bundle = extract(entry, tmp_path)

    assert is_valid("ExtractionBundle", bundle)


def test_stages_extract_records_kreuzberg_adapter_identity(
    tmp_path: Path, fake_kreuzberg: None
) -> None:
    _, entry = _write_pdf(tmp_path)

    bundle = extract(entry, tmp_path)

    assert bundle["adapter"]["name"] == "kreuzberg"
    assert bundle["adapter"]["version"] == "stub"


def test_stages_extract_propagates_sha256_and_path(
    tmp_path: Path, fake_kreuzberg: None
) -> None:
    _, entry = _write_pdf(tmp_path)

    bundle = extract(entry, tmp_path)

    assert bundle["source_path"] == entry["path"]
    assert bundle["source_sha256"] == entry["sha256"]


def test_stages_extract_text_comes_from_kreuzberg_content(
    tmp_path: Path, fake_kreuzberg: None
) -> None:
    _, entry = _write_pdf(tmp_path)

    bundle = extract(entry, tmp_path)

    assert bundle["content"]["text"] == "hello world"
    assert bundle["content"]["layout"] == []
