---
title: ADR-0009 — 10 contracts with 5 simplified stubs
purpose: Records the decision to ship all 10 contract slots now, with five speculative schemas reduced to minimal stubs
created: 2026-05-25
updated: 2026-05-25
validated_links: 2026-05-25
category: technical
---

## Status

Accepted — 2026-05-25

## Context and Problem Statement

The pipeline has 10 identified contract slots in the stage graph. Five are
substantive and load-bearing now: `DiscoveryManifest`, `ExtractionBundle`,
`CanonicalDoc`, `AnalysisReport`, `EvalReport`. Five are speculative and not
yet wired to any stage: `ClassificationManifest`, `FormatMatch`,
`FormatConformance`, `InputFormat`, `OutputFormat`. Shipping all 10 slots now
versus deferring the speculative five has implications for slot numbering
stability as the roadmap unfolds.

## Decision Drivers

- Slot-number stability: contract names referenced externally must not be
  renumbered when stubs are promoted to full schemas
- Minimal stub cost is low; a Pydantic `BaseModel` subclass with no fields
  is a valid placeholder
- The `REGISTRY` in `models/__init__.py` is registry-driven; adding a model
  later requires only a field addition, not a renaming pass

## Considered Options

### Option 1 — 10 slots, 5 as minimal stubs

- Good, because slot numbering is stable; no renaming churn when stubs are
  promoted
- Good, because the `REGISTRY` is complete now; downstream consumers can
  reference all 10 names without breakage
- Bad, because five stub models carry no fields and generate trivial schemas
  until wired

### Option 2 — Ship only the 5 substantive contracts now

- Good, because no dead-weight stubs in the codebase
- Bad, because adding the 5 speculative contracts later may require
  renumbering if slots are taken by interim additions
- Bad, because consumers that reference a future contract name get an import
  error until it ships

### Option 3 — Defer stub creation until each is needed

- Good, because zero maintenance until the need is concrete
- Bad, because risks contract-name collisions and breaks the slot ordering
  established in the stage graph
- Bad, because each addition is a breaking change for any consumer already
  enumerating the `REGISTRY`

## Decision Outcome

Chosen: **Option 1**. All 10 models are registered in `REGISTRY` in
`src/doc_pipeline_engine/models/__init__.py`. The 5 substantive models
(`DiscoveryManifest`, `ExtractionBundle`, `CanonicalDoc`, `AnalysisReport`,
`EvalReport`) have full field definitions. The 5 stubs
(`ClassificationManifest`, `FormatMatch`, `FormatConformance`, `InputFormat`,
`OutputFormat`) are minimal `BaseModel` subclasses. The roadmap documents
when each stub gets wired.

## More Information

- ADR-0001 (contracts as public API): [0001-pydantic-as-contract-source-of-truth.md](0001-pydantic-as-contract-source-of-truth.md)
- ADR-0007 (two-surface split): [0007-two-surface-split-engine-and-control-plane.md](0007-two-surface-split-engine-and-control-plane.md)
