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

CONTRACTS_DIR = Path(__file__).resolve().parents[3] / "contracts"

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
