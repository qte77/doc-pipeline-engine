# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Schema round-trip tests: every contract loads as valid JSON Schema, and
a minimal valid instance round-trips. Also: known-invalid instances fail.

This is the v0.1 contract floor - if these pass, any adapter / stage can be
wired against a stable contract surface.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import jsonschema
import pytest

from doc_pipeline_engine.base.contracts import (
    CONTRACTS_DIR,
    SCHEMA_NAMES,
    is_valid,
    load_schema,
    validate,
)

SHA_ZERO = "0" * 64
NOW = datetime.now(timezone.utc).isoformat()


@pytest.mark.parametrize("name", SCHEMA_NAMES)
def test_schema_file_exists(name: str) -> None:
    assert (CONTRACTS_DIR / f"{name}.schema.json").exists()


@pytest.mark.parametrize("name", SCHEMA_NAMES)
def test_schema_is_valid_jsonschema(name: str) -> None:
    schema = load_schema(name)
    jsonschema.Draft202012Validator.check_schema(schema)


# ---- Minimal valid instances --------------------------------------------


def _min_discovery() -> dict:
    return {
        "version": "0.1.0",
        "source": {"root": "/tmp/x", "kind": "folder"},
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


def _min_classification() -> dict:
    return {
        "version": "0.1.0",
        "items": [
            {"path": "a.pdf", "domain": "generic", "confidence": 0.9}
        ],
    }


def _min_extraction() -> dict:
    return {
        "version": "0.1.0",
        "source_path": "a.pdf",
        "source_sha256": SHA_ZERO,
        "adapter": {"name": "claude_cli_adapter", "version": "0.1.0"},
        "extracted_at": NOW,
        "content": {
            "text": "hello",
            "layout": [
                {
                    "kind": "heading",
                    "page": 1,
                    "bbox": [0.0, 0.0, 10.0, 10.0],
                    "level": 1,
                    "text": "Title",
                }
            ],
        },
    }


def _min_canonical() -> dict:
    return {
        "version": "0.1.0",
        "source_sha256": SHA_ZERO,
        "built_at": NOW,
        "root": {
            "id": "s.0",
            "level": 0,
            "kind": "doc",
            "text": "",
            "children": [
                {"id": "s.1", "level": 1, "kind": "section", "title": "T", "text": "body"}
            ],
        },
        "tier_summary": {"l0": "doc summary", "l1": "longer summary"},
    }


def _min_analysis() -> dict:
    return {
        "version": "0.1.0",
        "source_sha256": SHA_ZERO,
        "analyzed_at": NOW,
        "claims": [
            {"id": "c1", "text": "x is y", "node_refs": ["s.1"]}
        ],
        "entities": [],
    }


def _min_evaluation_report() -> dict:
    return {
        "version": "0.1.0",
        "evaluated_at": NOW,
        "tier": "quick",
        "verdict": "pass",
        "scores": {
            "schema_valid": {"value": 1.0, "threshold": 1.0, "passed": True}
        },
    }


def _min_format_match() -> dict:
    return {
        "version": "0.1.0",
        "matches": [
            {"format_id": "generic/any-document", "confidence": 0.5}
        ],
    }


def _min_format_conformance() -> dict:
    return {
        "version": "0.1.0",
        "output_format_id": "generic/technical-report-md",
        "conformant": True,
    }


def _min_input_format() -> dict:
    return {
        "id": "generic/any-document",
        "version": "0.1.0",
        "file_types": ["pdf", "docx", "txt", "md"],
    }


def _min_output_format() -> dict:
    return {
        "id": "generic/technical-report-md",
        "version": "0.1.0",
        "tier": "quick",
    }


MIN_INSTANCES = {
    "DiscoveryManifest": _min_discovery,
    "ClassificationManifest": _min_classification,
    "ExtractionBundle": _min_extraction,
    "CanonicalDoc": _min_canonical,
    "AnalysisReport": _min_analysis,
    "EvalReport": _min_evaluation_report,
    "FormatMatch": _min_format_match,
    "FormatConformance": _min_format_conformance,
    "InputFormat": _min_input_format,
    "OutputFormat": _min_output_format,
}


@pytest.mark.parametrize("name", SCHEMA_NAMES)
def test_min_valid_instance_roundtrips(name: str) -> None:
    instance = MIN_INSTANCES[name]()
    validate(name, instance)
    reloaded = json.loads(json.dumps(instance))
    assert is_valid(name, reloaded)


# ---- Known-invalid instances (schema drift / missing required) ----------


def test_extraction_missing_required_field_fails() -> None:
    bad = _min_extraction()
    del bad["content"]
    assert not is_valid("ExtractionBundle", bad)


def test_extraction_extra_field_fails_closed() -> None:
    bad = _min_extraction()
    bad["unknown_field"] = "surprise"
    assert not is_valid("ExtractionBundle", bad)


def test_canonical_requires_tier_summary() -> None:
    bad = _min_canonical()
    del bad["tier_summary"]
    assert not is_valid("CanonicalDoc", bad)


def test_analysis_requires_at_least_one_claim() -> None:
    bad = _min_analysis()
    bad["claims"] = []
    assert not is_valid("AnalysisReport", bad)


def test_input_format_id_must_be_pack_slash_format() -> None:
    bad = _min_input_format()
    bad["id"] = "no-slash-here"
    assert not is_valid("InputFormat", bad)


def test_output_format_needs_tier() -> None:
    bad = _min_output_format()
    del bad["tier"]
    assert not is_valid("OutputFormat", bad)


def test_discovery_sha256_must_be_hex_64() -> None:
    bad = _min_discovery()
    bad["files"][0]["sha256"] = "not-a-hash"
    assert not is_valid("DiscoveryManifest", bad)


def test_evaluation_verdict_enum() -> None:
    bad = _min_evaluation_report()
    bad["verdict"] = "maybe"
    assert not is_valid("EvalReport", bad)
