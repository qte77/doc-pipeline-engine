# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Tests for the docs/contracts.md generator.

The generator walks `doc_pipeline_engine.models.REGISTRY` and emits a
markdown reference: one section per model, JSON Schema dump, and
prose summary of `Field(description=...)` payloads. External
evaluators (Anthropic SDK + CC CLI/SDK) read this artifact so their
one-shot summaries can structurally match the pipeline's output.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

from doc_pipeline_engine.models import REGISTRY

REPO_ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "_gen_contracts_md", REPO_ROOT / "scripts" / "gen_contracts_md.py"
)
assert _spec
assert _spec.loader
_gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gen)


def test_gen_contracts_md_emits_section_per_model_in_registry() -> None:
    output = _gen.render()

    for name in REGISTRY:
        assert f"## {name}" in output, f"missing section for {name}"


def test_gen_contracts_md_includes_json_schema_block_per_model() -> None:
    output = _gen.render()

    # Each model should have a fenced JSON block with its emitted JSON Schema.
    # Count fenced ```json blocks: must be at least one per model.
    fenced_count = output.count("```json")
    assert fenced_count >= len(REGISTRY), (
        f"expected ≥{len(REGISTRY)} JSON Schema blocks, found {fenced_count}"
    )


def test_gen_contracts_md_includes_field_description_for_documented_field() -> None:
    output = _gen.render()

    # CanonicalDoc.source_sha256 carries Field(pattern=..., description ...) but
    # description is not set there. Pick a field with a known non-empty
    # description: Node.id has description="Stable node id (e.g. 's.1.2.3')".
    # The generator should surface that string in the prose summary.
    assert "Stable node id" in output, (
        "Field(description=...) payloads must appear in the rendered prose"
    )
