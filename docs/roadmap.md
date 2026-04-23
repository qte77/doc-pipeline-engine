# Roadmap

## 0.1.0 — Contracts

**Status**: done

Schemas define the interface between every pipeline stage. Nothing runs without them.

**Delivered**:

- 10 JSON schemas in `contracts/` (5 core, 5 reserved stubs)
- Gate validator (`src/doc_pipeline_engine/base/contracts.py`)
- Schema round-trip tests (38 tests)
- Sample download script (~95 files across 8 categories)
- Architecture and roadmap docs
- Apache-2.0 license with NOTICE for third-party content
- CI: CodeQL, Dependabot, CodeFactor

## 0.2.0 — Runner

Stage chain that passes JSON between stages in-process. Minimum viable pipeline.

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
- Failure tests (F1–F12)
- Orchestration bench (P1–P4)

## Future

- Fine-tuning pipeline
- Graph-RAG
- Certification packages (ISO 13485, IEC 62304, 21 CFR Part 11)
- CAD/LOB ingest
