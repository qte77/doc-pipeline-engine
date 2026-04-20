"""Schema loader + validator — the single entry point for all gate checks.

The 10 JSON schemas in contracts/ are the load-bearing design; every stage emits
JSON that must validate against exactly one of them.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import jsonschema

CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "contracts"

SCHEMA_NAMES: tuple[str, ...] = (
    "DiscoveryManifest",
    "ClassificationManifest",
    "ExtractionBundle",
    "CanonicalDoc",
    "AnalysisReport",
    "EvalReport",
    "FormatMatch",
    "FormatConformance",
    "InputFormat",
    "OutputFormat",
)


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict[str, Any]:
    """Load a JSON schema by short name (e.g. 'ExtractionBundle')."""
    path = CONTRACTS_DIR / f"{name}.schema.json"
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {path}")
    with path.open() as f:
        return json.load(f)


def validate(name: str, instance: Any) -> None:
    """Raise jsonschema.ValidationError on mismatch."""
    schema = load_schema(name)
    jsonschema.validate(instance=instance, schema=schema)


def is_valid(name: str, instance: Any) -> bool:
    """Non-raising form — returns True/False."""
    try:
        validate(name, instance)
        return True
    except jsonschema.ValidationError:
        return False
