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

## Design decisions

**Apache-2.0 over MIT** — Apache-2.0 includes patent grant and NOTICE file support. NOTICE is needed because `samples/` bundles third-party content under mixed licenses (CC-BY, Public Domain, IETF Trust, EU reuse).

**Hatchling over setuptools** — lighter, faster, PEP 621 native. `uv sync` replaces pip everywhere.

**10 contracts, 5 simplified** — all 10 schemas kept to reserve contract slots. Five speculative schemas (ClassificationManifest, FormatMatch, FormatConformance, InputFormat, OutputFormat) reduced to minimal stubs. Roadmap documents when each gets wired.

**Samples gitignored** — ~95 binary files too large for git. Download script is the single source of truth — carries metadata (URL, license, description) and generates `samples/SAMPLES.md` on each run.
