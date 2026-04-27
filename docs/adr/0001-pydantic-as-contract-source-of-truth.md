---
title: ADR-0001 — Pydantic as the contract source of truth
purpose: Records the decision to delete contracts/*.schema.json and make Pydantic v2 models the single source of truth for stage contracts
created: 2026-04-27
updated: 2026-04-27
validated_links: 2026-04-27
category: technical
---

**Status**: Accepted (2026-04-27)

## Context

§0.1.0 shipped 10 JSON Schema files under `contracts/` as the
load-bearing interface between every pipeline stage, validated at gate
boundaries via `jsonschema`. Stages emitted/consumed plain
`dict[str, Any]` — Python code never saw a typed object.

Three pressures pushed for a typed-model layer:

1. **Editor support / refactoring safety** — `dict[str, Any]` gives
   no field completion, no type-check on consumers, no signal when a
   contract field is renamed.
2. **mkdocs API rendering** — the planned mkdocs-material site
   (§0.2.2) wants per-contract documentation generated alongside
   stage docstrings. JSON Schema files don't render natively in
   mkdocstrings; Pydantic models with `Field(description=...)` do.
3. **Two sources of truth** — keeping JSON Schemas + a parallel
   Python type layer would mean every contract change had to
   touch both, with CI required to detect drift.

## Decision

**Pydantic v2 models are the single source of truth.** The 10 files
under `contracts/` are deleted; their content is reproduced as
Pydantic `BaseModel` definitions under
`src/doc_pipeline_engine/models/`, one file per contract.

The JSON Schema view stays available on demand:

- `python -m doc_pipeline_engine.models dump <Name>` prints the
  emitted `Model.model_json_schema()` to stdout.
- `from doc_pipeline_engine.models import REGISTRY` exposes
  `{name: BaseModel}` for programmatic consumers.

The gate API in `base/contracts.py` keeps its public shape
(`validate(name, instance)` and `is_valid(name, instance)`) so the
30+ existing call sites in `tests/` and `runner.py` work unchanged.
Internally both dispatch into `Model.model_validate(...)` and raise a
new `ContractValidationError` (with a `.message` attribute matching
the old `jsonschema.ValidationError` shape that `runner.run` reads).

## Rejected alternatives

- **Keep JSON Schemas authoritative; codegen Pydantic stubs from
  them** (e.g. via `datamodel-code-generator`). Rejected: loses
  Pydantic's expressive validators (`@field_validator`,
  `@model_validator`), adds a codegen step on every contract change,
  and leaves the wire format frozen at whatever the schema said —
  including its inconsistencies.
- **Hybrid (both authoritative)**. Rejected: divergence risk; CI
  drift checks become load-bearing.
- **Keep both authoritative; regenerate JSON in CI from models.**
  Rejected: extra build step, no consumer benefit once a CLI dump
  exposes the schema, and the on-disk files would still get stale
  reads in IDEs / GitHub blob view.

## Consequences

- The §0.1.0 wire format is no longer pinned to a hand-written file.
  Any field change is visible only in the model diff. **Mitigation**:
  every model carries snapshot smoke tests in
  `tests/test_models_schema_snapshot.py` over the emitted JSON
  Schema's `required` set + `additionalProperties: false` invariant;
  drift is caught at PR review.
- Runtime dependency: `pydantic>=2.7` added; `jsonschema` removed.
  Net runtime size is comparable.
- Downstream consumers that previously read `contracts/*.schema.json`
  via path must switch to either importing the model
  (`from doc_pipeline_engine.models import CanonicalDoc`) or shelling
  out to `python -m doc_pipeline_engine.models dump CanonicalDoc`.
  No such consumers exist inside this repo as of §0.2.1; the
  gha-llms-txt template did not link the schemas.
- Stage signatures still return `dict[str, Any]`. Full typed
  signatures are deferred to a §0.2.1-followup PR to keep this PR
  focused on the architectural shift; the AHA principle in
  `.claude/rules/core-principles.md` warned against doing both at
  once.

## Sources

- Pydantic v2 docs: <https://docs.pydantic.dev/latest/>
- mkdocstrings Pydantic rendering: <https://mkdocstrings.github.io/python/usage/configuration/general/>
