# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V2 render: AnalysisReport → RenderArtifacts via Jinja2 + render_artifacts."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from doc_pipeline_engine.render.formats import RenderArtifacts, render_artifacts

_TEMPLATE_DIR = Path(__file__).parent / "_jinja_templates"
_TEMPLATE_NAME = "quick_summary.md.j2"


def _load_env() -> Any:
    try:
        from jinja2 import (  # type: ignore[import-not-found]
            Environment,
            FileSystemLoader,
            select_autoescape,
        )
    except ImportError as e:
        raise RuntimeError(
            "Jinja2 not installed. Install with: uv sync --extra v2"
        ) from e
    # Reason: output is Markdown, not HTML — escaping `<` `>` `&` would
    # corrupt valid Markdown. select_autoescape([]) makes the no-escape
    # choice explicit and satisfies bandit B701.
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        keep_trailing_newline=True,
        autoescape=select_autoescape([]),
    )


def render_local(report: dict[str, Any], title: str = "Quick Summary") -> RenderArtifacts:
    """AnalysisReport → RenderArtifacts (md + docx + pdf)."""
    env = _load_env()
    template = env.get_template(_TEMPLATE_NAME)
    md = template.render(claims=report["claims"], entities=report.get("entities", []))
    return render_artifacts(md, title=title)
