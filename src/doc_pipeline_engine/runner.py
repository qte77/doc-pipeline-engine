# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Stage chain runner with gate validation.

A stage is a 3-tuple ``(name, callable, output_contract_name)``. The runner
threads the output of each stage into the next, validating the output
against its declared contract via `base.contracts.validate`. The chain
halts on the first validation failure with a `PipelineError` carrying the
offending stage name and contract.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import jsonschema

from doc_pipeline_engine.base.contracts import validate

StageCallable = Callable[[dict[str, Any]], dict[str, Any]]
Stage = tuple[str, StageCallable, str]


class PipelineError(Exception):
    """Raised when a stage output fails its contract gate."""

    def __init__(self, stage_name: str, contract_name: str, detail: str) -> None:
        self.stage_name = stage_name
        self.contract_name = contract_name
        self.detail = detail
        super().__init__(
            f"stage={stage_name!r} contract={contract_name!r}: {detail}"
        )


def run(stages: list[Stage], seed: dict[str, Any]) -> list[dict[str, Any]]:
    """Execute stages in order, validating each output against its contract."""
    outputs: list[dict[str, Any]] = []
    current: dict[str, Any] = seed
    for stage_name, fn, contract_name in stages:
        result = fn(current)
        try:
            validate(contract_name, result)
        except jsonschema.ValidationError as e:
            raise PipelineError(stage_name, contract_name, e.message) from e
        outputs.append(result)
        current = result
    return outputs
