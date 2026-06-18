# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V1 normalize: ExtractionBundle → CanonicalDoc via Claude API."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from doc_pipeline_engine.models.canonical_doc import CanonicalDoc
from doc_pipeline_engine.stages._anthropic_sdk_client import (
    MODEL_DEFAULT,
    _ClaudeClient,
    call_json,
)

_SYSTEM = """You are a document-structure normalizer. Convert an
ExtractionBundle's text content into a hierarchical CanonicalDoc tree.

Return JSON ONLY (no prose). Required top-level keys:
  - root: a tree node {id, level, kind, text, children?}
    - root must have id="s.0", level=0, kind="doc", text=""
    - children are nodes with kind in {"section","paragraph","heading","list","table"}
    - each non-root node has a unique id and a positive level
  - tier_summary: {l0: <≤3-sentence Quick-tier summary>,
                   l1: <longer Comprehensive-tier summary>}
"""


def normalize_anthropic_sdk(
    bundle: dict[str, Any],
    model: str = MODEL_DEFAULT,
    client: _ClaudeClient | None = None,
) -> CanonicalDoc:
    """Convert ExtractionBundle → CanonicalDoc via a Claude turn."""
    source_sha256 = bundle["source_sha256"] if isinstance(bundle, dict) else bundle.source_sha256
    text = bundle["content"]["text"] if isinstance(bundle, dict) else bundle.content.text
    user = (
        f"ExtractionBundle source_sha256: {source_sha256}\n\n"
        f"Extracted text:\n{text}"
    )
    payload = call_json(client, model=model, system=_SYSTEM, user=user)
    return CanonicalDoc.model_validate({
        "source_sha256": source_sha256,
        "built_at": datetime.now(UTC).isoformat(),
        "root": payload["root"],
        "tier_summary": payload["tier_summary"],
    })
