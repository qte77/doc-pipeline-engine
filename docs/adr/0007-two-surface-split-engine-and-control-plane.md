---
title: ADR-0007 — Two-surface split: engine (data plane) and control plane
purpose: Records the decision to separate the pipeline engine from any orchestration control plane
created: 2026-05-25
updated: 2026-05-25
validated_links: 2026-05-25
category: technical
---

## Status

Accepted — 2026-05-25

## Context and Problem Statement

The engine handles heavy Python work: extraction, validation, and rendering.
An orchestration layer — Claude Code plugins, agent skill chains, or any
other orchestrator — owns skills, hooks, and agent lifecycle. Conflating the
two surfaces would couple their release cycles and force consumers who only
need document processing to take on orchestration dependencies they don't
need. The architecture documents a "standalone by design" principle: no hard
dependencies on any orchestrator; contracts are the public API.

## Decision Drivers

- Engine must be embeddable without an orchestrator (polyforge, any CLI
  consumer, or plain Python import)
- Control plane needs to evolve independently; agent patterns (P1–P4) are
  still being evaluated
- Contracts as the public API make the boundary explicit and
  orchestration-agnostic

## Considered Options

### Option 1 — Two-surface split: engine as data plane, optional control plane

- Good, because engine stays lightweight and version-independent
- Good, because any orchestrator that can consume/produce the JSON contracts
  can participate
- Good, because control plane can change orchestration pattern (P1–P4)
  without touching engine internals
- Bad, because the boundary must be maintained deliberately; contract drift
  could still couple the two layers

### Option 2 — Integrated single surface

- Good, because simpler initial setup; one import, one lifecycle
- Bad, because couples control plane and data plane release cycles
- Bad, because bloats the engine for consumers that need only document
  processing

### Option 3 — Thin engine with heavyweight orchestrator dependency

- Good, because orchestrator provides rich tooling out of the box
- Bad, because forces dependency direction inward; engine is no longer
  standalone
- Bad, because consumers inherit the orchestrator's transitive dependency
  graph

## Decision Outcome

Chosen: **Option 1**. The engine exposes the 10 contracts as its only public
surface. Orchestration lives entirely outside: Claude Code plugins, polyforge,
or any system that can consume JSON. The four orchestration patterns (P1–P4)
evaluated in `docs/architecture.md` all operate on the same stage graph via
this split.

## More Information

- Architecture — standalone by design: [../architecture.md](../architecture.md)
- ADR-0009 (10 contracts): [0009-ten-contracts-with-five-simplified-stubs.md](0009-ten-contracts-with-five-simplified-stubs.md)
