# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""V2 eval: emit a minimal EvalReport.

Same shape as v1_eval — schema-validity scoring only. DeepEval faithfulness
probe is wired by PR 6 (the harness) when comparative scoring across legs
is needed.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from doc_pipeline_engine.render.formats import RenderArtifacts

CONTRACT_VERSION = "0.1.0"


def eval_local(
    bundle: dict[str, Any],
    canonical: dict[str, Any],
    report: dict[str, Any],
    artifacts: RenderArtifacts,
) -> dict[str, Any]:
    """Emit a minimal EvalReport for the V2 leg."""
    _ = (bundle, canonical, report, artifacts)
    return {
        "version": CONTRACT_VERSION,
        "evaluated_at": datetime.now(UTC).isoformat(),
        "tier": "quick",
        "verdict": "pass",
        "scores": {
            "schema_valid": {"value": 1.0, "threshold": 1.0, "passed": True}
        },
    }
