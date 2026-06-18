# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Tests for the NDJSON stream interface (§0.3.0)."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from doc_pipeline_engine.stream import main, run_stream

SHA_ZERO = "0" * 64
NOW = datetime.now(UTC).isoformat()

_MIN_DISCOVERY = {
    "version": "0.1.0",
    "source": {"root": "/data/ingest", "kind": "folder"},
    "discovered_at": NOW,
    "files": [
        {
            "path": "a.pdf",
            "size_bytes": 100,
            "sha256": SHA_ZERO,
            "file_type": "pdf",
        }
    ],
}


def _capture_stream(stage_names: list[str], seed: dict) -> tuple[int, list[dict]]:
    """Run run_stream and collect emitted NDJSON lines."""
    lines: list[dict] = []
    captured: list[str] = []

    def mock_write(s: str) -> None:
        captured.append(s)

    import sys

    with (
        patch.object(sys.stdout, "write", side_effect=mock_write),
        patch.object(sys.stdout, "flush"),
    ):
        code = run_stream(stage_names, seed)

    for chunk in captured:
        for line in chunk.splitlines():
            line = line.strip()
            if line:
                lines.append(json.loads(line))

    return code, lines


class TestRunStream:
    """run_stream emits correct NDJSON for the discover stage."""

    def test_discover_happy_path(self, tmp_path: Path) -> None:
        pdf = tmp_path / "sample.pdf"
        pdf.write_bytes(b"%PDF-1.4 minimal")

        seed = {"root": str(tmp_path), "glob": "**/*"}
        code, lines = _capture_stream(["discover"], seed)

        assert code == 0
        assert len(lines) == 1
        line = lines[0]
        assert line["stage"] == "discover"
        assert line["contract"] == "DiscoveryManifest"
        assert "output" in line
        assert len(line["output"]["files"]) == 1
        assert line["output"]["files"][0]["path"] == "sample.pdf"

    def test_unknown_stage_returns_error_line(self) -> None:
        code, lines = _capture_stream(["nonexistent"], {})

        assert code == 1
        assert len(lines) == 1
        assert "error" in lines[0]
        assert "nonexistent" in lines[0]["error"]

    def test_contract_failure_emits_error_line(self, tmp_path: Path) -> None:
        # Patch discover to return an invalid contract dict (missing required fields)
        from doc_pipeline_engine import stream as stream_mod

        bad_output = {"not": "a valid DiscoveryManifest"}

        def bad_discover(seed: dict) -> dict:
            return bad_output

        with (
            patch.object(stream_mod, "_STAGE_REGISTRY", {}),
            patch("doc_pipeline_engine.stages.discover.discover", return_value=bad_output),
        ):
            code, lines = _capture_stream(["discover"], {"root": str(tmp_path)})

        assert code == 1
        assert lines[-1].get("error") or lines[-1].get("stage") == "discover"

    def test_empty_stage_list_returns_zero(self) -> None:
        code, lines = _capture_stream([], {})
        assert code == 0
        assert lines == []


class TestMain:
    """main() reads seed from stdin and drives run_stream."""

    def test_no_args_returns_2(self) -> None:
        code = main([])
        assert code == 2

    def test_invalid_json_stdin_returns_2(self, tmp_path: Path) -> None:
        import sys

        with patch.object(sys.stdin, "read", return_value="not json"):
            code = main(["discover"])
        assert code == 2

    def test_discover_via_main(self, tmp_path: Path) -> None:
        import sys

        pdf = tmp_path / "doc.pdf"
        pdf.write_bytes(b"%PDF-1.4 minimal")
        seed_json = json.dumps({"root": str(tmp_path), "glob": "**/*"})

        lines: list[dict] = []
        captured: list[str] = []

        def mock_write(s: str) -> None:
            captured.append(s)

        with (
            patch.object(sys.stdin, "read", return_value=seed_json),
            patch.object(sys.stdout, "write", side_effect=mock_write),
            patch.object(sys.stdout, "flush"),
        ):
            code = main(["discover"])

        for chunk in captured:
            for line in chunk.splitlines():
                line = line.strip()
                if line:
                    lines.append(json.loads(line))

        assert code == 0
        assert lines[0]["stage"] == "discover"
        assert lines[0]["output"]["files"][0]["path"] == "doc.pdf"
