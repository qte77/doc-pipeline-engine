# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""PaddleOCR-VL adapter stub — not yet implemented."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from doc_pipeline_engine.base.adapter import AdapterBase, register


class PaddleOcrAdapter(AdapterBase):
    """Stub adapter for PaddleOCR-VL (§0.4.0 deferred)."""

    name = "paddle_ocr"
    version = "0.0.0"

    def extract(self, manifest_file: dict[str, Any], source_root: Path) -> dict[str, Any]:
        """Not implemented — raises NotImplementedError."""
        raise NotImplementedError("PaddleOcrAdapter is not yet implemented (§0.4.0 stub)")


register(PaddleOcrAdapter())
