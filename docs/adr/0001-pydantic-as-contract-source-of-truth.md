---
title: ADR-0001 — Pydantic as the contract source of truth
purpose: Records the decision to delete contracts/*.schema.json and make Pydantic v2 models the single source of truth for stage contracts
created: 2026-04-27
updated: 2026-05-25
validated_links: 2026-05-25
category: technical
---

## Status

Accepted — 2026-04-27

## Context and Problem Statement

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

## Decision Drivers

- Editor support / refactoring safety: `dict[str, Any]` gives no field completion or rename signals
- mkdocs API rendering: Pydantic models with `Field(description=...)` render natively; JSON Schema files do not
- Two sources of truth: JSON Schema + Python type layer requires dual maintenance and CI drift detection

## Considered Options

### Option 1 — Pydantic v2 models as single source of truth

**Pros**

- Field completion, type-checking, and rename signals available in editors
- Pydantic models with `Field(description=...)` render natively in mkdocstrings
- Single point of change for every contract; no drift between schema and code
- Expressive validators (`@field_validator`, `@model_validator`) available

**Cons**

- §0.1.0 wire format is no longer pinned to a hand-written file; field changes are visible only in the model diff
- Downstream consumers that previously read `contracts/*.schema.json` via path must switch to importing the model or shelling out to the CLI dump command

### Option 2 — Keep JSON Schemas authoritative; codegen Pydantic stubs from them

**Pros**

- Wire format remains explicitly declared in hand-written schema files
- Existing JSON Schema tooling and consumers keep working unchanged

**Cons**

- Loses Pydantic's expressive validators (`@field_validator`, `@model_validator`)
- Adds a codegen step on every contract change
- Leaves the wire format frozen at whatever the schema said — including its inconsistencies

### Option 3 — Hybrid: both authoritative

**Pros**

- Retains JSON Schema as an explicit contract artifact alongside typed Python models

**Cons**

- Divergence risk; CI drift checks become load-bearing

### Option 4 — Keep both authoritative; regenerate JSON in CI from models

**Pros**

- On-disk JSON Schema files remain available for external tooling and IDE/GitHub blob view

**Cons**

- Extra build step with no consumer benefit once a CLI dump exposes the schema
- On-disk files would still get stale reads in IDEs / GitHub blob view

## Decision Outcome

Chosen: **Option 1 — Pydantic v2 models as single source of truth**. The 10 files
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

## Consequences

- The §0.1.0 wire format is no longer pinned to a hand-written file.
  Any field change is visible only in the model diff. **Mitigation**:
  `tests/test_models_round_trip.py` is the load-bearing safety net —
  any breaking field rename, removed required field, or relaxed
  `extra` policy makes the round-trip identity test fail. A separate
  `inline_snapshot` over the full emitted schema is queued for
  whenever an actionable drift-review need surfaces (per AHA: wait
  for the second occurrence before extracting).
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

## More Information

- Pydantic v2 docs: <https://docs.pydantic.dev/latest/>
- mkdocstrings Pydantic rendering: <https://mkdocstrings.github.io/python/usage/configuration/general/>
