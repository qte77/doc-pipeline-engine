# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Kreuzberg adapter — wraps the existing Kreuzberg-backed extract stage."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from doc_pipeline_engine.base.adapter import AdapterBase, register
from doc_pipeline_engine.stages.extract import extract as _kreuzberg_extract

if TYPE_CHECKING:
    from pathlib import Path


class KreuzbergAdapter(AdapterBase):
    """Extraction backend using the Kreuzberg library (opt-in extra)."""

    name = "kreuzberg"
    version = "0.1.0"

    def extract(self, manifest_file: dict[str, Any], source_root: Path) -> dict[str, Any]:
        """Delegate to the Kreuzberg-backed extract stage function."""
        return _kreuzberg_extract(manifest_file, source_root)


register(KreuzbergAdapter())
