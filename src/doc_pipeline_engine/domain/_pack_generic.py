# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Generic domain pack — light pilot, fully wired for §0.5."""
from __future__ import annotations

from doc_pipeline_engine.domain import DomainPack, register
from doc_pipeline_engine.domain.formats import register_input, register_output
from doc_pipeline_engine.models.input_format import InputFormat
from doc_pipeline_engine.models.output_format import OutputFormat

_INPUT_FORMATS = [
    InputFormat(id="generic/text", version="0.1.0", file_types=["txt", "md"]),
    InputFormat(id="generic/pdf", version="0.1.0", file_types=["pdf"]),
    InputFormat(
        id="generic/office",
        version="0.1.0",
        file_types=["docx", "xlsx", "pptx"],
    ),
    InputFormat(
        id="generic/image",
        version="0.1.0",
        file_types=["png", "jpg", "jpeg", "tiff", "bmp"],
    ),
]

_OUTPUT_FORMATS = [
    OutputFormat(id="generic/quick-summary", version="0.1.0", tier="quick"),
    OutputFormat(id="generic/comprehensive-report", version="0.1.0", tier="comprehensive"),
]

for _fmt in _INPUT_FORMATS:
    register_input(_fmt)
for _fmt in _OUTPUT_FORMATS:
    register_output(_fmt)

register(
    DomainPack(
        name="generic",
        policy="claude-api-extracted-only",
        input_format_ids=[f.id for f in _INPUT_FORMATS],
        output_format_ids=[f.id for f in _OUTPUT_FORMATS],
        extraction_confidence_threshold=0.7,
        prompts={
            "normalize": "Normalize this extracted text into clean markdown. Preserve headings, lists, and tables. Remove headers, footers, and page numbers.",
            "analyze": "Analyze the document and identify its main claims, key entities, and section structure.",
            "draft": "Write a concise quick-tier summary (3 sentences max) capturing the document's gist.",
        },
    )
)
