# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Mechanical / electrical certification domain pack — declared stub for §0.5."""
from __future__ import annotations

from doc_pipeline_engine.domain import DomainPack, register

register(
    DomainPack(
        name="mech-elec-cert",
        policy="local-only",
        input_format_ids=[],
        output_format_ids=[],
        extraction_confidence_threshold=0.85,
        prompts={},
    )
)
