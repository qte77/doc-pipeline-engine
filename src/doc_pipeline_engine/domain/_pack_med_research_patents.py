# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Medical / research / patents domain pack — declared stub for §0.5."""
from __future__ import annotations

from doc_pipeline_engine.domain import DomainPack, register

register(
    DomainPack(
        name="med-research-patents",
        policy="cloud-redacted",
        input_format_ids=[],
        output_format_ids=[],
        extraction_confidence_threshold=0.9,
        prompts={},
    )
)
