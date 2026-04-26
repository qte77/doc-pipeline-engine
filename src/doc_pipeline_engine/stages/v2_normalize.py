# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V2 normalize: ExtractionBundle → CanonicalDoc, deterministic.

Kreuzberg's text is plain-text without layout structure, so the canonical
tree is a single section containing the extracted text. tier_summary is a
deterministic head-of-text excerpt — Quick tier (l0) takes the first 200
chars, Comprehensive (l1) the first 1000.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

CONTRACT_VERSION = "0.1.0"
_L0_CHARS = 200
_L1_CHARS = 1000


def _truncate(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n].rstrip() + "…"


def normalize_v2(bundle: dict[str, Any]) -> dict[str, Any]:
    """ExtractionBundle → CanonicalDoc dict, deterministic."""
    text = bundle["content"]["text"]
    return {
        "version": CONTRACT_VERSION,
        "source_sha256": bundle["source_sha256"],
        "built_at": datetime.now(timezone.utc).isoformat(),
        "root": {
            "id": "s.0",
            "level": 0,
            "kind": "doc",
            "text": "",
            "children": [
                {"id": "s.1", "level": 1, "kind": "section", "text": text},
            ],
        },
        "tier_summary": {
            "l0": _truncate(text, _L0_CHARS),
            "l1": _truncate(text, _L1_CHARS),
        },
    }
