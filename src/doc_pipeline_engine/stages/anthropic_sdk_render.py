# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V1 render: AnalysisReport → RenderArtifacts via Claude API.

Claude writes a 1-page Markdown summary; the shared render_artifacts
utility converts it to DOCX + PDF deterministically. The A/B with V2
is purely about the Markdown content quality.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from doc_pipeline_engine.render.formats import RenderArtifacts, render_artifacts
from doc_pipeline_engine.stages._anthropic_sdk_client import (
    MODEL_DEFAULT,
    _ClaudeClient,
    call_text,
)

if TYPE_CHECKING:
    from doc_pipeline_engine.models.analysis_report import AnalysisReport

_SYSTEM = """You are a document summarizer. Given an AnalysisReport
(claims + entities), write a 1-page Markdown summary suitable for the
Quick tier.

Output MARKDOWN ONLY (no prose, no JSON, no fences). Use:
  # for the document title
  ## for major sections
  - bullet lists for claims
  Plain paragraphs for prose.
"""


def render_anthropic_sdk(
    report: AnalysisReport,
    model: str = MODEL_DEFAULT,
    client: _ClaudeClient | None = None,
    title: str = "Quick Summary",
) -> RenderArtifacts:
    """AnalysisReport → RenderArtifacts (md + docx + pdf)."""
    data = report.model_dump(mode="json")
    user = (
        f"AnalysisReport source_sha256: {data['source_sha256']}\n\n"
        f"Claims:\n{json.dumps(data['claims'])}\n\n"
        f"Entities:\n{json.dumps(data['entities'])}"
    )
    md = call_text(client, model=model, system=_SYSTEM, user=user)
    return render_artifacts(md, title=title)
