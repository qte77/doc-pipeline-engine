---
title: ADR-0003 — Rename pipeline legs `v1` → `anthropic_sdk`, `v2` → `local`
purpose: Records the leg-naming refactor that replaces PR-ordering labels with self-describing names ahead of the external-evaluator work in §0.2.3
created: 2026-04-27
updated: 2026-04-27
validated_links: 2026-04-27
category: technical
---

**Status**: Accepted (2026-04-27)

## Context

The two pipeline legs have lived under `v1` / `v2` names since
§0.2.0. Those labels describe **PR-ordering** — the Anthropic-SDK
pipeline was scaffolded first, the local-tools pipeline second —
not what the legs actually do. As surface area grows (and a third
external comparison track lands in §0.2.3), the labels obscure
more than they describe:

- A reader has to look up "is v1 the LLM one or the Python one?"
  every time they touch the codebase.
- The Anthropic SDK leg's transport flexibility (vendor-agnostic
  via `base_url`, Bedrock, Vertex, or local LLM gateways) isn't
  signalled by `v1`.
- The local leg's defining property — "no LLM, no cloud calls" —
  isn't signalled by `v2`.
- The §0.2.3 external-evaluator work introduces a third comparison
  surface; calling it `v3` would compound the confusion.

## Decision

Rename the legs **before** the external evaluators land:

- `v1` → **`anthropic_sdk`** — describes the transport (Anthropic
  Python SDK), which can point at Anthropic cloud, Bedrock, Vertex,
  or any Anthropic-compatible endpoint via `base_url`.
- `v2` → **`local`** — describes the defining locality property
  (no LLM, no cloud calls; uses Tesseract OCR + optional spaCy NER,
  neither of which is an LLM).

Mechanical renames (via `git mv` to preserve history):

- `src/doc_pipeline_engine/stages/v1_*.py` →
  `stages/anthropic_sdk_*.py` (4 stage files +
  `_v1_client.py` → `_anthropic_sdk_client.py`).
- `src/doc_pipeline_engine/stages/v2_*.py` →
  `stages/local_*.py` (4 stage files).
- `tests/test_stages_v{1,2}_*.py` →
  `tests/test_stages_{anthropic_sdk,local}_*.py`.
- `tests/test_v1_client_backend_dispatch.py` →
  `tests/test_anthropic_sdk_client_backend_dispatch.py`.

Identifier renames inside those files:

- Functions: `normalize_v1` / `analyze_v1` / `render_v1` /
  `eval_v1` → `*_anthropic_sdk`. Same for `v2` → `local`.
- `harness.py`: `_run_v1_leg` / `_run_v2_leg` →
  `_run_anthropic_sdk_leg` / `_run_local_leg`. `DiffReport.v1` /
  `.v2` fields → `.anthropic_sdk` / `.local`. Variant strings
  `"v1"` / `"v2"` → `"anthropic_sdk"` / `"local"`. Axes keys
  `v1_total_seconds` / `v2_total_seconds` /
  `latency_ratio_v1_over_v2` → `anthropic_sdk_total_seconds` /
  `local_total_seconds` /
  `latency_ratio_anthropic_sdk_over_local`. CLI flag
  `--v1-model` → `--anthropic-sdk-model`.
- `pyproject.toml` extras: `v1` → `anthropic_sdk`, `v2` → `local`,
  `v2-render` → `local-render`, `v2-eval` → `local-eval`. The old
  names ship as **deprecated aliases** for one release cycle so
  existing devcontainer scripts and CI configs keep working.
- `Makefile`: `install_v2_nlp` → `install_local_nlp`. Old name
  kept as a deprecated alias for one release cycle.

Output directories:

- `outputs/<sha>/v1/` → `outputs/<sha>/anthropic_sdk/`.
- `outputs/<sha>/v2/` → `outputs/<sha>/local/`.

(Existing locally cached outputs from prior runs need a one-time
manual rename — `mv outputs/<sha>/v1 outputs/<sha>/anthropic_sdk`
— or fresh runs to regenerate; the harness writes to the new
paths after this PR.)

## Rejected alternatives

- **`api` / `local`** — `api` understates the SDK's transport
  flexibility (the SDK isn't married to Anthropic cloud).
- **`sdk` / `tools`** — pure mechanism naming; loses the locality
  signal `local` carries (and the cloud-by-default signal
  `anthropic_sdk` carries).
- **`llm` / `local`** — `llm` is generic enough to confuse with
  external-evaluator variants that also use LLMs (CC, external
  Anthropic SDK).
- **Glossary-only — keep `v1` / `v2` in code, add a doc table
  mapping** — smallest diff, but every new contributor would still
  have to look up the mapping. The opacity remains.

## Consequences

- **Forward-looking docs** (architecture, roadmap, CONTRIBUTING,
  prototype plan/samples, landscape, CHANGELOG) update to use the
  new names. **Historical results docs** (run-1 / run-2 / run-3)
  keep their `v1` / `v2` wording — they're frozen snapshots;
  retroactively editing them would falsify the records.
- The deprecated extras + Makefile aliases give downstream users
  one release cycle to migrate; CI green stays.
- The external-evaluator work in §0.2.3 references the new names
  from the start, avoiding a mixed-terminology PR.
- The `outputs/<sha>/<variant>/` directory rename is a small
  operational cost for users with cached local outputs;
  acceptable.

## Sources

- Plan file:
  [`doc-pipeline-external-evals-and-leg-rename.md`](https://github.com/qte77/doc-pipeline-engine/issues)
  (kept locally; tracked in this conversation).
- §0.2.3 external evaluators (the work this rename precedes):
  ADR-0004 (lands with the next PR).
