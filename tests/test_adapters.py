# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Tests for the adapter registry and concrete adapter implementations (§0.4.0)."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from doc_pipeline_engine.base.adapter import AdapterBase, available, get, register
from doc_pipeline_engine.base.contracts import is_valid

SHA_ZERO = "0" * 64

_FILE_ENTRY = {
    "path": "sample.pdf",
    "size_bytes": 100,
    "sha256": SHA_ZERO,
    "file_type": "pdf",
}


class TestRegistry:
    """Adapter registry: register, get, available."""

    def test_get_unknown_raises_key_error(self) -> None:
        with pytest.raises(KeyError, match="Unknown adapter"):
            get("__nonexistent__")

    def test_register_and_get_roundtrip(self) -> None:
        class _DummyAdapter(AdapterBase):
            name = "__test_dummy__"
            version = "0.0.0"

            def extract(self, manifest_file, source_root):
                return {}

        inst = _DummyAdapter()
        register(inst)
        assert get("__test_dummy__") is inst

    def test_available_returns_sorted_list(self) -> None:
        names = available()
        assert names == sorted(names)
        assert isinstance(names, list)

    def test_builtin_adapters_lazy_load(self) -> None:
        for name in ("kreuzberg", "claude_cli", "docling", "glm_ocr", "paddle_ocr"):
            adapter = get(name)
            assert adapter.name == name


class TestKreuzbergAdapter:
    """KreuzbergAdapter delegates to the kreuzberg stage function."""

    def test_extract_delegates_to_stage(self, tmp_path: Path) -> None:
        from doc_pipeline_engine.stages._adapters.kreuzberg import KreuzbergAdapter

        fake_bundle = {
            "version": "0.1.0",
            "source_path": "sample.pdf",
            "source_sha256": SHA_ZERO,
            "adapter": {"name": "kreuzberg", "version": "1.0"},
            "extracted_at": "2026-01-01T00:00:00+00:00",
            "content": {"text": "hello", "layout": []},
        }
        adapter = KreuzbergAdapter()
        target = "doc_pipeline_engine.stages._adapters.kreuzberg._kreuzberg_extract"
        with patch(target, return_value=fake_bundle):
            result = adapter.extract(_FILE_ENTRY, tmp_path)

        assert result == fake_bundle
        assert is_valid("ExtractionBundle", result)


class TestClaudeCliAdapter:
    """ClaudeCliAdapter shells out to claude --print --bare."""

    def _make_envelope(self, text: str) -> bytes:
        payload = {
            "result": text,
            "usage": {"input_tokens": 10, "output_tokens": 20},
            "model": "claude-opus-4-8",
        }
        return json.dumps(payload).encode()

    def test_extract_happy_path(self, tmp_path: Path) -> None:
        from doc_pipeline_engine.stages._adapters.claude_cli import ClaudeCliAdapter

        pdf = tmp_path / "sample.pdf"
        pdf.write_bytes(b"%PDF-1.4")

        fake_result = MagicMock()
        fake_result.returncode = 0
        fake_result.stdout = self._make_envelope("Extracted text content.")
        fake_result.stderr = b""

        adapter = ClaudeCliAdapter()
        with patch("subprocess.run", return_value=fake_result):
            result = adapter.extract({"path": "sample.pdf", "sha256": SHA_ZERO}, tmp_path)

        assert result["content"]["text"] == "Extracted text content."
        assert result["adapter"]["name"] == "claude_cli"
        assert is_valid("ExtractionBundle", result)

    def test_extract_missing_cli_raises_runtime_error(self, tmp_path: Path) -> None:
        from doc_pipeline_engine.stages._adapters.claude_cli import ClaudeCliAdapter

        pdf = tmp_path / "sample.pdf"
        pdf.write_bytes(b"%PDF-1.4")

        adapter = ClaudeCliAdapter()
        with (
            patch("subprocess.run", side_effect=FileNotFoundError("claude not found")),
            pytest.raises(RuntimeError, match="Claude Code CLI not found"),
        ):
            adapter.extract({"path": "sample.pdf", "sha256": SHA_ZERO}, tmp_path)

    def test_extract_nonzero_exit_raises_runtime_error(self, tmp_path: Path) -> None:
        from doc_pipeline_engine.stages._adapters.claude_cli import ClaudeCliAdapter

        pdf = tmp_path / "sample.pdf"
        pdf.write_bytes(b"%PDF-1.4")

        fake_result = MagicMock()
        fake_result.returncode = 1
        fake_result.stdout = b""
        fake_result.stderr = b"auth error"

        adapter = ClaudeCliAdapter()
        with (
            patch("subprocess.run", return_value=fake_result),
            pytest.raises(RuntimeError, match="claude exited 1"),
        ):
            adapter.extract({"path": "sample.pdf", "sha256": SHA_ZERO}, tmp_path)

    def test_extract_invalid_json_falls_back_to_raw(self, tmp_path: Path) -> None:
        from doc_pipeline_engine.stages._adapters.claude_cli import ClaudeCliAdapter

        pdf = tmp_path / "sample.pdf"
        pdf.write_bytes(b"%PDF-1.4")

        fake_result = MagicMock()
        fake_result.returncode = 0
        fake_result.stdout = b"plain text output"
        fake_result.stderr = b""

        adapter = ClaudeCliAdapter()
        with patch("subprocess.run", return_value=fake_result):
            result = adapter.extract({"path": "sample.pdf", "sha256": SHA_ZERO}, tmp_path)

        assert result["content"]["text"] == "plain text output"


class TestStubAdapters:
    """Stub adapters raise NotImplementedError."""

    @pytest.mark.parametrize("name", ["docling", "glm_ocr", "paddle_ocr"])
    def test_stub_raises_not_implemented(self, name: str, tmp_path: Path) -> None:
        adapter = get(name)
        with pytest.raises(NotImplementedError):
            adapter.extract(_FILE_ENTRY, tmp_path)
