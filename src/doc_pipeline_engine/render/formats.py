# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Markdown → DOCX + PDF conversion.

Imports for ``markdown``, ``docx``, and ``weasyprint`` are deferred so this
module loads without the ``render`` extra. Calling ``render_artifacts``
without the extra raises a clear hint to install it.
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass
from typing import Any

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


@dataclass
class RenderArtifacts:
    md: str
    docx: bytes
    pdf: bytes


def _import_or_raise() -> tuple[Any, Any, Any]:
    try:
        import markdown as md_lib  # type: ignore[import-not-found]
        from docx import Document  # type: ignore[import-not-found]
        from weasyprint import HTML  # type: ignore[import-not-found]
    except ImportError as e:
        raise RuntimeError(
            "Render extras not installed. Install with: uv sync --extra render"
        ) from e
    return md_lib, Document, HTML


def _markdown_to_docx_bytes(md_source: str, title: str, document_cls: Any) -> bytes:
    """Build a DOCX programmatically from Markdown.

    Quick-tier scope only: headings (``#``..``######``) become Word headings,
    everything else becomes a paragraph. Blank lines split blocks.
    """
    doc = document_cls()
    doc.core_properties.title = title
    for block in md_source.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        match = _HEADING_RE.match(block)
        if match:
            level = len(match.group(1))
            doc.add_heading(match.group(2).strip(), level=level)
        else:
            doc.add_paragraph(block)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _markdown_to_pdf_bytes(md_source: str, md_lib: Any, html_cls: Any) -> bytes:
    html = md_lib.markdown(md_source)
    return html_cls(string=html).write_pdf()


def render_artifacts(markdown_source: str, title: str) -> RenderArtifacts:
    """Convert Markdown to DOCX (python-docx) and PDF (markdown→html→WeasyPrint).

    The Markdown source is returned unchanged; DOCX and PDF are byte payloads.
    Deterministic for a given library version set.
    """
    md_lib, document_cls, html_cls = _import_or_raise()
    return RenderArtifacts(
        md=markdown_source,
        docx=_markdown_to_docx_bytes(markdown_source, title, document_cls),
        pdf=_markdown_to_pdf_bytes(markdown_source, md_lib, html_cls),
    )
