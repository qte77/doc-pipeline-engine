# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V2 render stage tests. Needs jinja2 + render extras."""
from __future__ import annotations

import pytest

pytest.importorskip("jinja2")
pytest.importorskip("docx")
pytest.importorskip("markdown")
pytest.importorskip("weasyprint")

from doc_pipeline_engine.render.formats import RenderArtifacts  # noqa: E402
from doc_pipeline_engine.stages.v2_render import render_v2  # noqa: E402

SHA = "0" * 64


def _report(claims: list[dict] | None = None, entities: list[dict] | None = None) -> dict:
    return {
        "version": "0.1.0",
        "source_sha256": SHA,
        "analyzed_at": "2026-04-26T00:00:00+00:00",
        "claims": claims or [{"id": "c1", "text": "x is y", "node_refs": ["s.1"]}],
        "entities": entities or [],
    }


def test_stages_v2_render_returns_render_artifacts() -> None:
    art = render_v2(_report())

    assert isinstance(art, RenderArtifacts)
    assert art.docx[:4] == b"PK\x03\x04"
    assert art.pdf[:5] == b"%PDF-"


def test_stages_v2_render_md_contains_claim_text() -> None:
    claim = {"id": "c1", "text": "Sky is blue.", "node_refs": ["s.1"]}

    art = render_v2(_report(claims=[claim]))

    assert "Sky is blue." in art.md
    assert "## Key Claims" in art.md


def test_stages_v2_render_md_omits_entities_section_when_empty() -> None:
    art = render_v2(_report(entities=[]))

    assert "## Entities" not in art.md


def test_stages_v2_render_md_includes_entities_section_when_present() -> None:
    entities = [{"id": "e1", "name": "Acme", "kind": "org"}]

    art = render_v2(_report(entities=entities))

    assert "## Entities" in art.md
    assert "**Acme**" in art.md
    assert "(org)" in art.md
