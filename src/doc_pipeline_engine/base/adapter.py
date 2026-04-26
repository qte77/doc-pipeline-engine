# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Adapter ABC for extraction backends.

An adapter consumes a single file entry from a `DiscoveryManifest` and emits
an `ExtractionBundle`. Concrete adapters live in `stages/` (e.g. Kreuzberg).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AdapterBase(ABC):
    name: str
    version: str

    @abstractmethod
    def extract(self, manifest_file: dict[str, Any]) -> dict[str, Any]:
        """Convert one DiscoveryManifest file entry to an ExtractionBundle dict."""
        ...
