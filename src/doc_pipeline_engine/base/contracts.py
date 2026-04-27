# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Contract gate — Pydantic-backed validator dispatcher.

The 10 Pydantic models in :mod:`doc_pipeline_engine.models` are the single
source of truth. ``validate(name, instance)`` and ``is_valid(name,
instance)`` keep the original API so existing call sites keep working;
both dispatch into the model registry.
"""
from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from doc_pipeline_engine.models import REGISTRY

SCHEMA_NAMES: tuple[str, ...] = tuple(sorted(REGISTRY))


class ContractValidationError(Exception):
    """Raised when an instance fails its contract gate.

    Carries a ``.message`` attribute matching the legacy
    ``jsonschema.ValidationError`` shape that ``runner.run()`` reads.
    """

    def __init__(self, name: str, error: ValidationError) -> None:
        self.name = name
        self.message = str(error)
        super().__init__(f"{name}: {self.message}")


def validate(name: str, instance: Any) -> None:
    """Validate ``instance`` against the named contract; raise on mismatch.

    Args:
        name: Contract short name (e.g. ``"ExtractionBundle"``).
        instance: dict or Pydantic model instance to validate.

    Raises:
        KeyError: if ``name`` is not a known contract.
        ContractValidationError: if ``instance`` does not match.
    """
    model = REGISTRY[name]
    try:
        model.model_validate(instance)
    except ValidationError as e:
        raise ContractValidationError(name, e) from e


def is_valid(name: str, instance: Any) -> bool:
    """Return ``True`` iff ``instance`` matches the named contract."""
    try:
        validate(name, instance)
    except ContractValidationError:
        return False
    return True
