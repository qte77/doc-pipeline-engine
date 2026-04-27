# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V1 render stage tests with stubbed Anthropic client.

Render extras are required for the underlying converter; tests skip
cleanly without them.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

pytest.importorskip("docx")
pytest.importorskip("markdown")
pytest.importorskip("weasyprint")

from doc_pipeline_engine.render.formats import RenderArtifacts  # noqa: E402
from doc_pipeline_engine.stages.anthropic_sdk_render import render_anthropic_sdk  # noqa: E402

SHA = "0" * 64
_MD = "# Summary\n\nClaude wrote this."


def _stub_client(response_text: str) -> object:
    def _create(**_kwargs: object) -> object:
        return SimpleNamespace(content=[SimpleNamespace(text=response_text)])

    return SimpleNamespace(messages=SimpleNamespace(create=_create))


def _report() -> dict:
    return {
        "version": "0.1.0",
        "source_sha256": SHA,
        "analyzed_at": "2026-04-26T00:00:00+00:00",
        "claims": [{"id": "c1", "text": "x", "node_refs": ["s.1"]}],
        "entities": [],
    }


def test_stages_v1_render_returns_render_artifacts() -> None:
    client = _stub_client(_MD)

    art = render_anthropic_sdk(_report(), client=client)

    assert isinstance(art, RenderArtifacts)
    assert art.md == _MD
    assert art.docx[:4] == b"PK\x03\x04"
    assert art.pdf[:5] == b"%PDF-"
