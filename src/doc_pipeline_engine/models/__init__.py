# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Pydantic v2 models for the 10 stage contracts.

Each model is the single source of truth for its contract; ``REGISTRY`` maps
the contract's short name to its model class so the gate validator and the
``python -m doc_pipeline_engine.models dump`` CLI stay registry-driven.
"""
from __future__ import annotations

from pydantic import BaseModel

from .analysis_report import AnalysisReport
from .canonical_doc import CanonicalDoc
from .classification import ClassificationManifest
from .discovery_manifest import DiscoveryManifest
from .eval_report import EvalReport
from .extraction_bundle import ExtractionBundle
from .format_conformance import FormatConformance
from .format_match import FormatMatch
from .input_format import InputFormat
from .output_format import OutputFormat

REGISTRY: dict[str, type[BaseModel]] = {
    "AnalysisReport": AnalysisReport,
    "CanonicalDoc": CanonicalDoc,
    "ClassificationManifest": ClassificationManifest,
    "DiscoveryManifest": DiscoveryManifest,
    "EvalReport": EvalReport,
    "ExtractionBundle": ExtractionBundle,
    "FormatConformance": FormatConformance,
    "FormatMatch": FormatMatch,
    "InputFormat": InputFormat,
    "OutputFormat": OutputFormat,
}

__all__ = [
    "REGISTRY",
    "AnalysisReport",
    "CanonicalDoc",
    "ClassificationManifest",
    "DiscoveryManifest",
    "EvalReport",
    "ExtractionBundle",
    "FormatConformance",
    "FormatMatch",
    "InputFormat",
    "OutputFormat",
]
