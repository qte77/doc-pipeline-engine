# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""CLI entry point: ``python -m doc_pipeline_engine.models dump <Name>``.

Replaces the deleted ``contracts/*.schema.json`` files for any consumer that
needs the JSON-Schema view; the model registry stays the single source of
truth.
"""
from __future__ import annotations

import argparse
import json
import sys

from . import REGISTRY


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m doc_pipeline_engine.models")
    sub = parser.add_subparsers(dest="cmd", required=True)
    dump = sub.add_parser("dump", help="Print a model's JSON Schema")
    dump.add_argument("name", help="Contract name, e.g. CanonicalDoc")
    sub.add_parser("list", help="List known contract names")

    args = parser.parse_args(argv)
    if args.cmd == "list":
        for name in sorted(REGISTRY):
            print(name)
        return 0
    if args.cmd == "dump":
        model = REGISTRY.get(args.name)
        if model is None:
            print(f"unknown contract: {args.name}", file=sys.stderr)
            print(f"known: {', '.join(sorted(REGISTRY))}", file=sys.stderr)
            return 2
        json.dump(model.model_json_schema(), sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(_cli())
