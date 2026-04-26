# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V1 analyze: CanonicalDoc → AnalysisReport via Claude API."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from doc_pipeline_engine.stages._v1_client import (
    MODEL_DEFAULT,
    _ClaudeClient,
    call_json,
)

CONTRACT_VERSION = "0.1.0"
ANALYZER_NAME = "v1_analyze_claude"

_SYSTEM = """You are a document analyzer. Extract key claims and entities
from a CanonicalDoc tree.

Return JSON ONLY. Required top-level keys:
  - claims: list of {id, text, node_refs[≥1], kind?, confidence?}, ≥1 item
  - entities: list of {id, name, kind, aliases?} (kind in
    person/org/product/standard/measurement/location/concept/other)

node_refs values must reference node ids present in the canonical tree.
"""


def analyze_v1(
    canonical: dict[str, Any],
    model: str = MODEL_DEFAULT,
    client: _ClaudeClient | None = None,
) -> dict[str, Any]:
    """CanonicalDoc → AnalysisReport via a Claude turn."""
    user = (
        f"CanonicalDoc source_sha256: {canonical['source_sha256']}\n\n"
        f"Canonical tree:\n{json.dumps(canonical['root'])}"
    )
    payload = call_json(client, model=model, system=_SYSTEM, user=user)
    return {
        "version": CONTRACT_VERSION,
        "source_sha256": canonical["source_sha256"],
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "analyzer": {"name": ANALYZER_NAME, "version": CONTRACT_VERSION, "model": model},
        "claims": payload["claims"],
        "entities": payload["entities"],
    }
