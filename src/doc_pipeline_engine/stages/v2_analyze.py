# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V2 analyze: CanonicalDoc → AnalysisReport, deterministic.

Claims come from a heading-walk over the canonical tree (first sentence of
each leaf node with text). Entities come from spaCy NER when available;
when spaCy is not installed, entities is an empty list (schema-permitted).
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

CONTRACT_VERSION = "0.1.0"
ANALYZER_NAME = "v2_analyze_local"

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")

_SPACY_KIND_MAP = {
    "PERSON": "person",
    "ORG": "org",
    "GPE": "location",
    "LOC": "location",
    "PRODUCT": "product",
    "LAW": "standard",
    "NORP": "standard",
    "DATE": "measurement",
    "TIME": "measurement",
    "QUANTITY": "measurement",
    "MONEY": "measurement",
    "PERCENT": "measurement",
}


def _walk_leaves(node: dict[str, Any]) -> list[dict[str, Any]]:
    children = node.get("children") or []
    if not children:
        return [node]
    out: list[dict[str, Any]] = []
    for child in children:
        out.extend(_walk_leaves(child))
    return out


def _first_sentence(text: str) -> str:
    parts = _SENTENCE_END.split(text.strip(), maxsplit=1)
    return parts[0].strip() if parts else ""


def _extract_claims(root: dict[str, Any]) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    for idx, leaf in enumerate(_walk_leaves(root), start=1):
        text = (leaf.get("text") or "").strip()
        if not text:
            continue
        claim_text = _first_sentence(text)
        if not claim_text:
            continue
        claims.append(
            {"id": f"c{idx}", "text": claim_text, "node_refs": [leaf["id"]]}
        )
    if not claims:
        # schema requires minItems=1; emit a degenerate claim from root
        claims.append(
            {"id": "c1", "text": "(no extractable claims)", "node_refs": [root["id"]]}
        )
    return claims


def _maybe_extract_entities(text: str) -> list[dict[str, Any]]:
    try:
        import spacy  # type: ignore[import-not-found]
    except ImportError:
        return []
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # model not downloaded — make install-models
        return []
    doc = nlp(text)
    entities: list[dict[str, Any]] = []
    seen: set[str] = set()
    for idx, ent in enumerate(doc.ents, start=1):
        key = (ent.text, ent.label_)
        if key in seen:
            continue
        seen.add(key)
        entities.append(
            {
                "id": f"e{idx}",
                "name": ent.text,
                "kind": _SPACY_KIND_MAP.get(ent.label_, "other"),
            }
        )
    return entities


def _gather_text(node: dict[str, Any]) -> str:
    parts: list[str] = []
    if node.get("text"):
        parts.append(node["text"])
    for child in node.get("children") or []:
        parts.append(_gather_text(child))
    return "\n\n".join(p for p in parts if p)


def analyze_v2(canonical: dict[str, Any]) -> dict[str, Any]:
    """CanonicalDoc → AnalysisReport dict, deterministic."""
    root = canonical["root"]
    return {
        "version": CONTRACT_VERSION,
        "source_sha256": canonical["source_sha256"],
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "analyzer": {"name": ANALYZER_NAME, "version": CONTRACT_VERSION},
        "claims": _extract_claims(root),
        "entities": _maybe_extract_entities(_gather_text(root)),
    }
