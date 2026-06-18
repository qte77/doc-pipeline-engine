# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V1 normalize stage tests with stubbed Anthropic client."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from types import SimpleNamespace

from doc_pipeline_engine.models.canonical_doc import CanonicalDoc
from doc_pipeline_engine.models.extraction_bundle import AdapterInfo, Content, ExtractionBundle
from doc_pipeline_engine.stages.anthropic_sdk_normalize import normalize_anthropic_sdk

SHA = "0" * 64

_VALID_CANONICAL_PAYLOAD = {
    "root": {
        "id": "s.0",
        "level": 0,
        "kind": "doc",
        "text": "",
        "children": [
            {"id": "s.1", "level": 1, "kind": "section", "title": "Intro", "text": "body"}
        ],
    },
    "tier_summary": {"l0": "quick summary", "l1": "longer summary"},
}


def _stub_client(response_text: str) -> object:
    def _create(**_kwargs: object) -> object:
        return SimpleNamespace(content=[SimpleNamespace(text=response_text)])

    return SimpleNamespace(messages=SimpleNamespace(create=_create))


def _bundle() -> ExtractionBundle:
    return ExtractionBundle(
        source_path="a.pdf",
        source_sha256=SHA,
        adapter=AdapterInfo(name="stub", version="0.0.0"),
        extracted_at=datetime.now(UTC).isoformat(),
        content=Content(text="hello world", layout=[]),
    )


def test_stages_v1_normalize_returns_canonical_doc_instance() -> None:
    client = _stub_client(json.dumps(_VALID_CANONICAL_PAYLOAD))

    canonical = normalize_anthropic_sdk(_bundle(), client=client)

    assert isinstance(canonical, CanonicalDoc)


def test_stages_v1_normalize_propagates_source_sha256() -> None:
    client = _stub_client(json.dumps(_VALID_CANONICAL_PAYLOAD))

    canonical = normalize_anthropic_sdk(_bundle(), client=client)

    assert canonical.source_sha256 == SHA
