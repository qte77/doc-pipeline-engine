# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V1 eval: emit a minimal EvalReport.

For v1 we only record schema-validity (1.0 if all upstream gates passed —
which the runner enforces). A faithfulness probe via Claude is left for
PR 6 (the harness) to add when comparative scoring across legs is wired.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from doc_pipeline_engine.render.formats import RenderArtifacts

CONTRACT_VERSION = "0.1.0"


def eval_anthropic_sdk(
    bundle: dict[str, Any],
    canonical: dict[str, Any],
    report: dict[str, Any],
    artifacts: RenderArtifacts,
) -> dict[str, Any]:
    """Emit a minimal EvalReport for the V1 leg."""
    _ = (bundle, canonical, report, artifacts)  # kept for symmetry with V2 signature
    return {
        "version": CONTRACT_VERSION,
        "evaluated_at": datetime.now(UTC).isoformat(),
        "tier": "quick",
        "verdict": "pass",
        "scores": {
            "schema_valid": {"value": 1.0, "threshold": 1.0, "passed": True}
        },
    }
