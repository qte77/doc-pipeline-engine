# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""NDJSON stream interface over the pipeline runner.

Each stage emits one JSON line to stdout::

    {"stage": "<name>", "contract": "<name>", "output": {...}}

On contract failure a single error line is emitted and the process exits
with code 1::

    {"stage": "<name>", "contract": "<name>", "error": "<detail>"}

Usage (seed from stdin, output to stdout)::

    echo '{"root": "/data/ingest", "glob": "**/*.pdf"}' | \\
        python -m doc_pipeline_engine.stream discover

``python -m doc_pipeline_engine.stream`` with no subcommand lists available
stage names.
"""
from __future__ import annotations

import json
import sys
from typing import Any

from doc_pipeline_engine.runner import PipelineError, Stage, run

_STAGE_REGISTRY: dict[str, Stage] = {}


def _discover_adapter(seed: dict[str, Any]) -> dict[str, Any]:
    """Unpack seed dict and call discover with typed args."""
    from pathlib import Path

    from doc_pipeline_engine.stages.discover import discover

    return discover(Path(seed["root"]), seed.get("glob", "**/*"))


def _extract_adapter(file_entry: dict[str, Any]) -> dict[str, Any]:
    """Unpack file_entry dict and call extract with typed args."""
    from pathlib import Path

    from doc_pipeline_engine.stages.extract import extract

    # file_entry must carry source_root; stream callers embed it in the seed
    source_root = Path(file_entry.get("source_root", "."))
    return extract(file_entry, source_root)


_ADAPTERS: dict[str, Any] = {
    "discover": _discover_adapter,
    "extract": _extract_adapter,
}


def _register(name: str, contract: str) -> None:
    """Register a stage adapter by name."""
    if name not in _ADAPTERS:
        raise KeyError(f"Unknown stage: {name!r}")
    _STAGE_REGISTRY[name] = (name, _ADAPTERS[name], contract)


_KNOWN: dict[str, str] = {
    "discover": "DiscoveryManifest",
    "extract": "ExtractionBundle",
}


def _emit(obj: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj, default=str) + "\n")
    sys.stdout.flush()


def run_stream(stage_names: list[str], seed: dict[str, Any]) -> int:
    """Run named stages in order, emitting one NDJSON line per stage.

    Args:
        stage_names: Ordered list of stage names to execute.
        seed: Initial input passed to the first stage.

    Returns:
        Exit code: 0 on success, 1 on contract failure.
    """
    stages: list[Stage] = []
    for name in stage_names:
        if name not in _KNOWN:
            _emit({"error": f"Unknown stage: {name!r}. Known: {sorted(_KNOWN)}"})
            return 1
        _register(name, _KNOWN[name])
        stages.append(_STAGE_REGISTRY[name])

    try:
        outputs = run(stages, seed)
    except PipelineError as exc:
        _emit({"stage": exc.stage_name, "contract": exc.contract_name, "error": exc.detail})
        return 1

    for (name, _fn, contract), output in zip(stages, outputs, strict=True):
        _emit({"stage": name, "contract": contract, "output": output})

    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: read seed from stdin, stream stage outputs to stdout.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Exit code.
    """
    args = argv if argv is not None else sys.argv[1:]

    if not args:
        known = ", ".join(sorted(_KNOWN))
        sys.stderr.write(f"Usage: doc-pipeline <stage> [<stage> ...]\nKnown stages: {known}\n")
        return 2

    try:
        seed = json.loads(sys.stdin.read())
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Invalid JSON on stdin: {exc}\n")
        return 2

    return run_stream(list(args), seed)


if __name__ == "__main__":
    sys.exit(main())
