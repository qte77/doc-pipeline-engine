# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""EvalReport model — Evaluate stage output (scores + gate verdict)."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._common import CONTRACT_VERSION_LITERAL, ContractVersion, StrictModel


class HarnessInfo(StrictModel):
    """Identifies the eval harness that produced the report."""

    name: Literal["smoke", "ragas", "trulens", "deepeval", "helm", "custom"] | None = None
    version: str | None = None


class Score(StrictModel):
    """One named metric value with optional threshold + pass/fail."""

    value: float
    threshold: float | None = None
    passed: bool | None = None
    notes: str | None = None


class Finding(StrictModel):
    """A single issue surfaced by the eval harness."""

    severity: Literal["info", "warn", "error"]
    message: str
    node_refs: list[str] | None = None


class EvalReport(StrictModel):
    """Evaluate stage output — scores + gate verdict.

    v0.1 = smoke; v0.2 = RAGAs/TruLens; v0.3 = HELM-style.
    """

    version: ContractVersion = CONTRACT_VERSION_LITERAL
    evaluated_at: str
    tier: Literal["quick", "comprehensive"]
    harness: HarnessInfo | None = None
    verdict: Literal["pass", "warn", "fail"]
    scores: dict[str, Score] = Field(
        description=(
            "Named metrics. Smoke eval includes at least schema_valid and faithfulness."
        ),
    )
    findings: list[Finding] | None = None
