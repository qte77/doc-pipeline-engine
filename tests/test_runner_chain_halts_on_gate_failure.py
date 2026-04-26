# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Runner chain behavior: passes valid outputs through, halts on first
gate failure, and surfaces stage and contract names in the error.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from doc_pipeline_engine.runner import PipelineError, run

SHA_ZERO = "0" * 64
NOW = datetime.now(timezone.utc).isoformat()


def _valid_discovery_manifest(_seed: dict) -> dict:
    return {
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


def _valid_extraction_bundle(_manifest: dict) -> dict:
    return {
        "version": "0.1.0",
        "source_path": "a.pdf",
        "source_sha256": SHA_ZERO,
        "adapter": {"name": "stub", "version": "0.0.0"},
        "extracted_at": NOW,
        "content": {"text": "hi", "layout": []},
    }


def _invalid_extraction_bundle(_manifest: dict) -> dict:
    bundle = _valid_extraction_bundle(_manifest)
    del bundle["content"]
    return bundle


def test_runner_chain_passes_valid_outputs_through_all_stages() -> None:
    stages = [
        ("discover", _valid_discovery_manifest, "DiscoveryManifest"),
        ("extract", _valid_extraction_bundle, "ExtractionBundle"),
    ]

    outputs = run(stages, seed={})

    assert len(outputs) == 2
    assert outputs[0]["files"][0]["path"] == "a.pdf"
    assert outputs[1]["adapter"]["name"] == "stub"


def test_runner_chain_halts_on_first_invalid_output() -> None:
    stages = [
        ("discover", _valid_discovery_manifest, "DiscoveryManifest"),
        ("extract", _invalid_extraction_bundle, "ExtractionBundle"),
    ]

    with pytest.raises(PipelineError):
        run(stages, seed={})


def test_runner_pipeline_error_contains_stage_and_contract_names() -> None:
    stages = [
        ("discover", _valid_discovery_manifest, "DiscoveryManifest"),
        ("extract", _invalid_extraction_bundle, "ExtractionBundle"),
    ]

    with pytest.raises(PipelineError) as exc:
        run(stages, seed={})

    assert exc.value.stage_name == "extract"
    assert exc.value.contract_name == "ExtractionBundle"
    assert "extract" in str(exc.value)
    assert "ExtractionBundle" in str(exc.value)
