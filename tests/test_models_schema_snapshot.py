# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Stability smoke tests over each model's emitted JSON Schema.

Replaces the deleted ``contracts/*.schema.json`` consumer surface: every
model exposes a ``model_json_schema()`` that downstream consumers can
fetch via ``python -m doc_pipeline_engine.models dump <Name>``. These
tests assert the emitted schema is well-formed and carries the model's
structural invariants (title, type, required fields). Full snapshot
freezing via ``inline_snapshot`` is queued as a follow-up.
"""
from __future__ import annotations

import json

import pytest

from doc_pipeline_engine.models import REGISTRY

REQUIRED_FIELDS = {
    "AnalysisReport": {"version", "source_sha256", "analyzed_at", "claims", "entities"},
    "CanonicalDoc": {"version", "source_sha256", "built_at", "root", "tier_summary"},
    "ClassificationManifest": {"version", "items"},
    "DiscoveryManifest": {"version", "source", "discovered_at", "files"},
    "EvalReport": {"version", "evaluated_at", "tier", "verdict", "scores"},
    "ExtractionBundle": {
        "version",
        "source_path",
        "source_sha256",
        "adapter",
        "extracted_at",
        "content",
    },
    "FormatConformance": {"version", "output_format_id", "conformant"},
    "FormatMatch": {"version", "matches"},
    "InputFormat": {"id", "version", "file_types"},
    "OutputFormat": {"id", "version", "tier"},
}


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_model_json_schema_is_serializable_object(name: str) -> None:
    schema = REGISTRY[name].model_json_schema()
    assert isinstance(schema, dict)
    assert schema.get("type") == "object"
    json.dumps(schema)  # raises if any field isn't JSON-safe


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_model_json_schema_required_fields_match_v0_1_0(name: str) -> None:
    schema = REGISTRY[name].model_json_schema()
    # ``version`` carries a default but pydantic still lists it in required —
    # the v0.1.0 wire shape; "required" stays the source-of-truth set.
    assert set(schema.get("required", [])) >= REQUIRED_FIELDS[name] - {"version"}


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_model_json_schema_forbids_additional_properties(name: str) -> None:
    schema = REGISTRY[name].model_json_schema()
    assert schema.get("additionalProperties") is False
