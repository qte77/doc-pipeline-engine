# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Format registry — maps FormatId strings to InputFormat / OutputFormat instances.

Packs declare format IDs; the registry holds the canonical definitions.
The registry is populated when domain pack modules are imported.
"""
from __future__ import annotations

from doc_pipeline_engine.models.input_format import InputFormat
from doc_pipeline_engine.models.output_format import OutputFormat

_INPUT: dict[str, InputFormat] = {}
_OUTPUT: dict[str, OutputFormat] = {}


def register_input(fmt: InputFormat) -> None:
    """Register an input format definition."""
    _INPUT[fmt.id] = fmt


def register_output(fmt: OutputFormat) -> None:
    """Register an output format definition."""
    _OUTPUT[fmt.id] = fmt


def get_input(format_id: str) -> InputFormat:
    """Return the named InputFormat.

    Raises:
        KeyError: if not registered.
    """
    if format_id not in _INPUT:
        raise KeyError(f"Unknown input format {format_id!r}. Known: {sorted(_INPUT)}")
    return _INPUT[format_id]


def get_output(format_id: str) -> OutputFormat:
    """Return the named OutputFormat.

    Raises:
        KeyError: if not registered.
    """
    if format_id not in _OUTPUT:
        raise KeyError(f"Unknown output format {format_id!r}. Known: {sorted(_OUTPUT)}")
    return _OUTPUT[format_id]


def available_inputs() -> list[str]:
    """Return sorted list of registered input format IDs."""
    return sorted(_INPUT)


def available_outputs() -> list[str]:
    """Return sorted list of registered output format IDs."""
    return sorted(_OUTPUT)
