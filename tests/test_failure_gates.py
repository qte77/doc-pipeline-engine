# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Failure-mode gate tests (§0.6.0).

Covers:
  F1  — corrupt/unreadable input → adapter raises, does not emit a bundle
  F4  — schema drift → contract gate rejects malformed stage output
  F5  — policy violation → PolicyGate rejects disallowed adapter
  F11 — format miss → FormatGate rejects file type not in pack
  F12 — required-section miss → contract gate rejects bundle missing field

F2 (adapter disagreement) is deferred: requires two real adapters running
against the same file (integration test, not unit test).
"""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from doc_pipeline_engine.base.contracts import is_valid
from doc_pipeline_engine.base.gates import ConfidenceGate, FormatGate, GateError, PolicyGate
from doc_pipeline_engine.runner import PipelineError, run

SHA_ZERO = "0" * 64
NOW = datetime.now(UTC).isoformat()

_VALID_BUNDLE = {
    "version": "0.1.0",
    "source_path": "a.pdf",
    "source_sha256": SHA_ZERO,
    "adapter": {"name": "stub", "version": "0.0.0"},
    "extracted_at": NOW,
    "content": {"text": "hello", "layout": []},
}


# ---------------------------------------------------------------------------
# F1 — Corrupt input: adapter raises, pipeline halts
# ---------------------------------------------------------------------------


class TestF1CorruptInput:
    """F1: corrupt or unreadable input propagates as a pipeline halt."""

    def test_kreuzberg_adapter_raises_on_corrupt_file(self, tmp_path: Path) -> None:
        corrupt = tmp_path / "corrupt.pdf"
        corrupt.write_bytes(b"NOT A PDF")

        from doc_pipeline_engine.stages._adapters.kreuzberg import KreuzbergAdapter

        adapter = KreuzbergAdapter()
        with patch(
            "doc_pipeline_engine.stages._adapters.kreuzberg._kreuzberg_extract",
            side_effect=RuntimeError("Kreuzberg: cannot parse file"),
        ):
            with pytest.raises(RuntimeError, match="Kreuzberg: cannot parse file"):
                adapter.extract(
                    {"path": "corrupt.pdf", "sha256": SHA_ZERO}, tmp_path
                )

    def test_runner_halts_when_extract_stage_raises(self) -> None:
        def _bad_extract(_manifest: dict) -> dict:
            raise RuntimeError("corrupt input")

        stages = [
            ("extract", _bad_extract, "ExtractionBundle"),
        ]
        with pytest.raises(RuntimeError, match="corrupt input"):
            run(stages, seed={})


# ---------------------------------------------------------------------------
# F4 — Schema drift: stage emits wrong type for a required field
# ---------------------------------------------------------------------------


class TestF4SchemaDrift:
    """F4: stage output with wrong field type is rejected by the contract gate."""

    def test_discovery_manifest_rejects_non_string_path(self) -> None:
        drifted = {
            "version": "0.1.0",
            "source": {"root": "/data", "kind": "folder"},
            "discovered_at": NOW,
            "files": [
                {
                    "path": 12345,  # int, not str — schema drift
                    "size_bytes": 100,
                    "sha256": SHA_ZERO,
                    "file_type": "pdf",
                }
            ],
        }
        assert not is_valid("DiscoveryManifest", drifted)

    def test_runner_halts_on_drifted_discovery_manifest(self) -> None:
        def _drifted_discover(_seed: dict) -> dict:
            return {
                "version": "0.1.0",
                "source": {"root": "/data", "kind": "folder"},
                "discovered_at": NOW,
                "files": [{"path": 99, "size_bytes": 100, "sha256": SHA_ZERO, "file_type": "pdf"}],
            }

        with pytest.raises(PipelineError) as exc:
            run([("discover", _drifted_discover, "DiscoveryManifest")], seed={})
        assert exc.value.contract_name == "DiscoveryManifest"


# ---------------------------------------------------------------------------
# F5 — Policy violation: cloud adapter + local-only pack
# ---------------------------------------------------------------------------


class TestF5PolicyViolation:
    """F5: PolicyGate rejects adapters disallowed by the pack's data-locality policy."""

    def test_claude_cli_rejected_by_local_only_pack(self) -> None:
        gate = PolicyGate("mech-elec-cert")
        with pytest.raises(GateError) as exc:
            gate.check("claude_cli")
        assert exc.value.gate == "F5-policy-violation"
        assert "claude_cli" in exc.value.detail
        assert "local-only" in exc.value.detail

    def test_kreuzberg_allowed_by_local_only_pack(self) -> None:
        gate = PolicyGate("mech-elec-cert")
        gate.check("kreuzberg")  # must not raise

    def test_claude_cli_allowed_by_claude_api_extracted_only_pack(self) -> None:
        gate = PolicyGate("generic")
        gate.check("claude_cli")  # must not raise

    def test_unknown_adapter_rejected_by_local_only_policy(self) -> None:
        # Unknown adapters have no locality attribute; treated as non-local
        # and therefore blocked under local-only policy.
        gate = PolicyGate("mech-elec-cert")
        with pytest.raises(GateError, match="F5-policy-violation"):
            gate.check("__unknown_adapter__")

    def test_unknown_adapter_allowed_by_permissive_policy(self) -> None:
        # Non-local-only policies permit any adapter (including unknown ones).
        gate = PolicyGate("generic")
        gate.check("__unknown_adapter__")  # must not raise


# ---------------------------------------------------------------------------
# F11 — Format miss: file type not in pack's accepted input formats
# ---------------------------------------------------------------------------


class TestF11FormatMiss:
    """F11: FormatGate rejects files whose type is not in the pack's input formats."""

    def test_svg_rejected_by_generic_pack(self) -> None:
        gate = FormatGate("generic")
        with pytest.raises(GateError) as exc:
            gate.check({"path": "diagram.svg", "sha256": SHA_ZERO, "file_type": "svg"})
        assert exc.value.gate == "F11-format-miss"
        assert "svg" in exc.value.detail

    def test_pdf_accepted_by_generic_pack(self) -> None:
        gate = FormatGate("generic")
        gate.check({"path": "doc.pdf", "sha256": SHA_ZERO, "file_type": "pdf"})

    def test_txt_accepted_by_generic_pack(self) -> None:
        gate = FormatGate("generic")
        gate.check({"path": "notes.txt", "sha256": SHA_ZERO, "file_type": "txt"})

    def test_unknown_type_rejected_by_generic_pack(self) -> None:
        gate = FormatGate("generic")
        with pytest.raises(GateError, match="F11-format-miss"):
            gate.check({"path": "data.xyz", "sha256": SHA_ZERO, "file_type": "xyz"})


# ---------------------------------------------------------------------------
# F12 — Required-section miss: ExtractionBundle missing required field
# ---------------------------------------------------------------------------


class TestF12RequiredSectionMiss:
    """F12: contract gate rejects ExtractionBundle missing a required field."""

    def test_bundle_missing_content_fails_validation(self) -> None:
        bundle = dict(_VALID_BUNDLE)
        del bundle["content"]
        assert not is_valid("ExtractionBundle", bundle)

    def test_bundle_missing_source_path_fails_validation(self) -> None:
        bundle = dict(_VALID_BUNDLE)
        del bundle["source_path"]
        assert not is_valid("ExtractionBundle", bundle)

    def test_runner_halts_on_bundle_missing_required_field(self) -> None:
        def _bad_bundle(_seed: dict) -> dict:
            b = dict(_VALID_BUNDLE)
            del b["content"]
            return b

        with pytest.raises(PipelineError) as exc:
            run([("extract", _bad_bundle, "ExtractionBundle")], seed={})
        assert exc.value.contract_name == "ExtractionBundle"


# ---------------------------------------------------------------------------
# ConfidenceGate (F2 partial)
# ---------------------------------------------------------------------------


class TestConfidenceGate:
    """ConfidenceGate rejects bundles below the pack threshold."""

    def test_low_confidence_rejected(self) -> None:
        gate = ConfidenceGate("generic")  # threshold 0.7
        with pytest.raises(GateError, match="G-extract-confidence"):
            gate.check({**_VALID_BUNDLE, "confidence": 0.5})

    def test_high_confidence_accepted(self) -> None:
        gate = ConfidenceGate("generic")
        gate.check({**_VALID_BUNDLE, "confidence": 0.9})  # must not raise

    def test_missing_confidence_accepted(self) -> None:
        gate = ConfidenceGate("generic")
        gate.check(_VALID_BUNDLE)  # confidence absent — must not raise
