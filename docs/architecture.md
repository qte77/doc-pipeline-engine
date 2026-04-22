# Architecture

## Core idea

Every pipeline stage consumes one JSON contract and emits another. A gate validator sits between each pair. If validation fails, the pipeline stops.

```text
stage(ContractA) → validate → stage(ContractB) → validate → ...
```

## Two runtime modes

**Runner** (0.2.0) — in-process stage chain. Python callables, direct function calls.

**Stream** (0.3.0) — NDJSON over stdin/stdout. Same stages, CLI-composable. Built on top of the runner.

```text
In-process:  runner.run([discover, extract, normalize, analyze, draft])
CLI:         discover | extract | normalize | analyze | draft
```

Both use the same contracts and the same gate validator.

## Stage graph

```text
Discover → ExtractionBundle → CanonicalDoc → AnalysisReport → EvalReport
         ↑                                                       ↓
   DiscoveryManifest                                        pass/warn/fail
```

Reserved stages (stub contracts, wired later):

- Classify → ClassificationManifest
- RecognizeInputFormat → FormatMatch
- CheckOutputConformance → FormatConformance
- Format definitions → InputFormat, OutputFormat

## Package layout

```text
contracts/                          JSON schemas (the load-bearing interface)
src/doc_pipeline_engine/
  base/contracts.py                 Schema loader + gate validator
  base/adapter.py                   Adapter ABC (0.4.0)
  runner.py                         Stage chain runner (0.2.0)
  cli.py                            NDJSON CLI wrappers (0.3.0)
  stages/                           Stage implementations (0.2.0+)
```

## Standalone by design

No hard dependencies on any orchestrator or consumer. Contracts are the public API. Any system that can produce/consume the JSON schemas can participate — polyforge, office-polyforge, Claude Code plugins, or anything else.
