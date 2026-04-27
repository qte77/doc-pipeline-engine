---
title: Roadmap
purpose: Versioned milestones (0.1 → 0.6+) with status, scope, and reasoning per release
created: 2026-04-23
updated: 2026-04-27
validated_links: 2026-04-26
category: requirements
---

## 0.1.0 — Contracts

**Status**: done

Schemas define the interface between every pipeline stage. Nothing runs without them.

**Delivered**:

- 10 JSON schemas in `contracts/` (5 core, 5 reserved stubs) — superseded by §0.2.1 (Pydantic models)
- Gate validator (`src/doc_pipeline_engine/base/contracts.py`)
- Schema round-trip tests (38 tests)
- Sample download script (~95 files across 8 categories)
- Architecture and roadmap docs
- Apache-2.0 license with NOTICE for third-party content
- CI: CodeQL, Dependabot, CodeFactor

## 0.2.0 — Runner

Stage chain that passes JSON between stages in-process. Minimum viable pipeline. Prototype walk-through: see [prototype/plan.md](prototype/plan.md).

**Why now**: contracts without a runner are just static files. The runner proves the contracts work as a real data flow.

**Goals**:

- Each stage is a callable: one contract in, one contract out
- Gate validation between every stage call
- Halt on first failure with actionable error
- Happy-path test on one sample through all stages

**Implementation**:

- `src/doc_pipeline_engine/runner.py` — ordered stage list, loop + validate
- Stage functions as a protocol/ABC (input contract type → output contract type)
- Wire stub stages that emit minimal valid contracts to prove the chain

## 0.2.1 — Typed contracts

**Status**: done

Pydantic v2 models replace the JSON-Schema gate. Models become the single source of truth; the JSON Schema view stays available on demand via a CLI dump for downstream consumers.

**Delivered**:

- `src/doc_pipeline_engine/models/` — 10 Pydantic v2 `BaseModel`s, one per contract; registry-driven (`REGISTRY` in `__init__.py`).
- `python -m doc_pipeline_engine.models dump <Name>` CLI — emits `Model.model_json_schema()` for any consumer that needs the JSON Schema view; replaces the deleted `contracts/*.schema.json` files.
- `base/contracts.py` rewritten as a Pydantic-backed thin wrapper (`validate(name, instance)` and `is_valid(name, instance)` keep the same public API).
- `runner.py` raises `PipelineError` from `ContractValidationError` (no longer depends on `jsonschema`).
- `tests/test_models_round_trip.py` — replaces the old `tests/test_contracts.py`. Round-trip identity per model is the load-bearing safety net for schema drift; full `inline_snapshot` over emitted schemas is deferred.
- ADR-0001 records the decision to make pydantic models the source of truth.

**Deferred to §0.2.1-followup**: full typed return signatures on stages (currently still `dict[str, Any]` to keep the test surface stable).

## 0.2.2 — API docs site

**Status**: in progress

mkdocs-material + mkdocstrings serves the public API reference and the existing prose tree on GitHub Pages. Pydantic `Field(description=...)` payloads from §0.2.1 render inline.

**Delivered**:

- `mkdocs.yaml` at repo root (mirrors `qte77/Agents-eval`); material theme with dual-palette `prefers-color-scheme` toggle; mkdocstrings + autorefs.
- `.github/workflows/generate-deploy-mkdocs-ghpages.yaml` — deploys via `actions/deploy-pages@v4` on PR-merged-to-main + `workflow_dispatch`.
- `[dependency-groups] docs` in `pyproject.toml` (`mkdocs`, `mkdocs-material`, `mkdocstrings[python]`, `mkdocs-autorefs`).
- `make docs`, `make docs_serve`, `make docs_index` Makefile targets.
- Google-style docstring pass on `src/doc_pipeline_engine/` enforced by ruff `D`-rules.
- Bird's-eye architecture SVG with `prefers-color-scheme` theming, embedded in `docs/architecture.md` and `README.md`.
- ADR-0002 records the decision.

## 0.3.0 — Stream

NDJSON (newline-delimited JSON) interface over the runner. Enables CLI composition, audit logging, and IPC.

**Why now**: runner proves in-process flow; stream wraps it for pipes, logging, and external consumers. Falls out naturally from 0.2.0.

**Goals**:

- Each stage readable/writable as a single JSON line on stdin/stdout
- Composable: `discover | extract | normalize | analyze | draft`
- Tee-friendly for audit trails and debugging
- Replay from any saved stream line

**Implementation**:

- Thin CLI wrapper per stage: read stdin → call stage function → write stdout
- Entry point in pyproject.toml (`doc-pipeline-engine` CLI or per-stage commands)
- Works with `jq`, any language, any consumer (polyforge, office-polyforge)

## 0.4.0 — Adapters

Real extraction backends plugged into the runner/stream.

**Why now**: runner and stream define how adapters get called. Building adapters before that means guessing the interface.

**Goals**:

- `claude_cli_adapter` wired end-to-end
- docling, GLM-OCR, PaddleOCR-VL as stubs with adapter ABC
- Cross-validation between adapters on same input

**Implementation**:

- Adapter ABC in `src/doc_pipeline_engine/base/adapter.py`
- Each adapter is a stage callable that emits `ExtractionBundle`
- Adapter registry for swap/fallback

## 0.5.0 — Domain packs

Pluggable per-domain config: policies, prompts, thresholds, input/output formats.

**Goals**:

- Generic pack fully wired
- mech-elec-cert and med-research-patents as declared stubs
- Format registry, ClassificationManifest / FormatMatch / FormatConformance wired
- Data-locality policies (local-only, claude-api-extracted-only, cloud-redacted)

## 0.6.0 — Eval

Evaluation harnesses and quality gates.

**Goals**:

- RAGAs / TruLens / DeepEval harness wrappers
- InputFormat / OutputFormat schemas wired
- Failure tests: F1 (corrupt PDF), F2 (adapter disagreement), F4 (schema drift), F5 (policy violation), F11 (format miss), F12 (required-section miss)
- Orchestration bench (P1–P4)

## Future

- Orchestration pattern evaluation (P1 skill chain, P2 subagents, P3 team mode, P4 hybrid)

- Fine-tuning pipeline
- Graph-RAG
- Certification packages (ISO 13485, IEC 62304, 21 CFR Part 11)
- CAD/LOB ingest
