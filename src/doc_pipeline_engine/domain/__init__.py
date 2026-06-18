# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Domain pack registry and DomainPack definition.

A domain pack is the pluggable per-domain configuration: policies, prompts,
extraction thresholds, and the input/output formats the domain supports.

Built-in packs (lazy-loaded on first access):

- ``generic``              — light pilot, fully wired for §0.5
- ``mech-elec-cert``       — stub
- ``med-research-patents`` — stub

Usage::

    from doc_pipeline_engine.domain import get

    pack = get("generic")
    print(pack.policy)          # "local-only" | "claude-api-extracted-only" | "cloud-redacted"
    print(pack.input_format_ids) # ["generic/text", "generic/pdf"]
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Policy = Literal["local-only", "claude-api-extracted-only", "cloud-redacted"]

_REGISTRY: dict[str, DomainPack] = {}

_BUILTIN: dict[str, str] = {
    "generic": "doc_pipeline_engine.domain._pack_generic",
    "mech-elec-cert": "doc_pipeline_engine.domain._pack_mech_elec_cert",
    "med-research-patents": "doc_pipeline_engine.domain._pack_med_research_patents",
}


@dataclass(frozen=True)
class DomainPack:
    """Immutable per-domain configuration bundle.

    Attributes:
        name: Short pack identifier (e.g. ``"generic"``).
        policy: Default data-locality policy for this domain.
        input_format_ids: Format IDs this pack accepts (must exist in the format registry).
        output_format_ids: Format IDs this pack can emit.
        extraction_confidence_threshold: Minimum adapter confidence accepted by gate G_extract.
        prompts: Keyed prompt strings injected at each stage.
    """

    name: str
    policy: Policy
    input_format_ids: list[str]
    output_format_ids: list[str]
    extraction_confidence_threshold: float = 0.7
    prompts: dict[str, str] = field(default_factory=dict)


def register(pack: DomainPack) -> None:
    """Register a domain pack under its ``name``."""
    _REGISTRY[pack.name] = pack


def get(name: str) -> DomainPack:
    """Return the named domain pack, lazy-loading built-ins on first access.

    Args:
        name: Pack name (e.g. ``"generic"``).

    Returns:
        The :class:`DomainPack` instance.

    Raises:
        KeyError: if ``name`` is not registered and not a known built-in.
    """
    if name not in _REGISTRY:
        if name not in _BUILTIN:
            known = sorted(set(_REGISTRY) | set(_BUILTIN))
            raise KeyError(f"Unknown domain pack {name!r}. Known: {known}")
        import importlib

        importlib.import_module(_BUILTIN[name])
    return _REGISTRY[name]


def available() -> list[str]:
    """Return names of all registered domain packs."""
    return sorted(_REGISTRY)
