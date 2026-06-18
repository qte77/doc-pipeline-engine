# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Adapter ABC and registry for extraction backends.

An adapter consumes one DiscoveryManifest file entry and emits an
ExtractionBundle dict. Concrete adapters register themselves via
:func:`register`; callers retrieve them with :func:`get`.

Built-in adapters (lazy-imported on first use):

- ``kreuzberg``   — Kreuzberg library (opt-in extra)
- ``claude_cli``  — Claude Code CLI headless one-shot
- ``docling``     — Docling (stub; not yet implemented)
- ``glm_ocr``     — GLM-OCR (stub; not yet implemented)
- ``paddle_ocr``  — PaddleOCR-VL (stub; not yet implemented)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


Locality = str
"""Data locality of an adapter: ``"local"`` (on-device) or ``"api"`` (external LLM call)."""


class AdapterBase(ABC):
    """Base class every extraction backend implements.

    Class attributes:
        name: Short adapter identifier registered in the adapter registry.
        version: Adapter implementation version string.
        locality: Data locality — ``"local"`` for on-device processing,
            ``"api"`` for adapters that call an external LLM API.
            Used by :class:`~doc_pipeline_engine.base.gates.PolicyGate` to
            enforce data-locality policies without a hardcoded allowlist.
    """

    name: str
    version: str
    locality: Locality = "local"

    @abstractmethod
    def extract(self, manifest_file: dict[str, Any], source_root: Path) -> dict[str, Any]:
        """Convert one DiscoveryManifest file entry to an ExtractionBundle dict.

        Args:
            manifest_file: One entry from ``DiscoveryManifest.files``.
            source_root: Absolute path to the folder that was discovered.

        Returns:
            A dict that validates against the ``ExtractionBundle`` contract.
        """
        ...


_REGISTRY: dict[str, AdapterBase] = {}

_BUILTIN: dict[str, str] = {
    "kreuzberg": "doc_pipeline_engine.stages._adapters.kreuzberg",
    "claude_cli": "doc_pipeline_engine.stages._adapters.claude_cli",
    "docling": "doc_pipeline_engine.stages._adapters.docling",
    "glm_ocr": "doc_pipeline_engine.stages._adapters.glm_ocr",
    "paddle_ocr": "doc_pipeline_engine.stages._adapters.paddle_ocr",
}


def register(adapter: AdapterBase) -> None:
    """Register an adapter instance under its ``name``."""
    _REGISTRY[adapter.name] = adapter


def get(name: str) -> AdapterBase:
    """Return the named adapter, lazy-loading built-ins on first access.

    Args:
        name: Adapter name (e.g. ``"kreuzberg"``).

    Returns:
        The registered :class:`AdapterBase` instance.

    Raises:
        KeyError: if ``name`` is not registered and not a known built-in.
    """
    if name not in _REGISTRY:
        if name not in _BUILTIN:
            known = sorted(set(_REGISTRY) | set(_BUILTIN))
            raise KeyError(f"Unknown adapter {name!r}. Known: {known}")
        import importlib

        importlib.import_module(_BUILTIN[name])
    return _REGISTRY[name]


def available() -> list[str]:
    """Return names of all registered adapters."""
    return sorted(_REGISTRY)
