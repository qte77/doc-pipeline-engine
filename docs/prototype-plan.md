# E2E Prototype Plan

First end-to-end walk-through of the [stage graph](architecture.md#stage-graph) on a single sample, run as **two parallel variants** so we can A/B Claude Code against the surveyed tools.

Scope: **Quick tier only** (see [architecture.md → Output tiers](architecture.md#output-tiers)). Comprehensive tier is deferred to [roadmap §0.5.0 — Domain packs](roadmap.md#050--domain-packs); prototyping it now would over-commit before we know which V1 stages already do the job.

## Goal

Same input sample → both variants → identical output contract shape → mechanical diff. Answer the question: *which stages does Claude Code already handle well enough, and which actually need the engine-layer tools?*

## Variant 1 — Claude Code + Anthropic API (Linux)

| Stage | How |
|---|---|
| Discover | `pathlib.rglob()` over `samples/` → `DiscoveryManifest` |
| Extract — PDF | `claude_cli_adapter` posts file via Messages API `documents` block; Claude returns JSON matching `ExtractionBundle` |
| Extract — DOCX/XLSX/PPTX | Preprocess with `python-docx` / `openpyxl` / `python-pptx` (flatten content), then Claude turn → `ExtractionBundle` |
| Normalize | Claude turn: `ExtractionBundle → CanonicalDoc` (heading tree + `tier_summary`) |
| Analyze | Claude turn over `CanonicalDoc.root` → `AnalysisReport` (top headings, key claims, top-N entities) |
| Render | Claude writes Quick-tier 1-page Markdown summary from `AnalysisReport` |
| Eval | Claude self-eval (schema check + 1 faithfulness probe) → `EvalReport` |

Anthropic's office-document skills (`anthropics/skills`) are Claude.ai-only — not invokable from Claude Code on Linux. Office formats need preprocessing libs.

## Variant 2 — Tools from the landscape

| Stage | How |
|---|---|
| Discover | `pathlib.rglob()` → `DiscoveryManifest` (shared with V1) |
| Extract | **docling** (PDF/Office), **Kreuzberg** (long tail) → `ExtractionBundle`. See [landscape-ingest.md](landscape-ingest.md). |
| Normalize | Thin Python adapter `DoclingDocument → CanonicalDoc` (adds `source_sha256`, `built_at`, runs tier-split). See [landscape-process.md → Normalization to CanonicalDoc](landscape-process.md#5-normalization-to-canonicaldoc). |
| Analyze | **spaCy** NER over `root` text nodes → `AnalysisReport` (heading walk for key claims; no RAG at Quick tier). See [landscape-process.md → Entity extraction / NER](landscape-process.md#3-entity-extraction--ner). |
| Render | **Jinja2** template → 1-page Markdown. See [landscape-output.md](landscape-output.md). |
| Eval | Schema gates + **DeepEval** or **RAGAs** for faithfulness → `EvalReport`. See [roadmap §0.6.0 — Eval](roadmap.md#060--eval). |

## Eval axes

Both variants emit valid contracts at every gate (see [architecture.md → Core idea](architecture.md#core-idea)). A small harness (~100 LOC) runs both legs on the same sample and diffs:

1. **Faithfulness** — does the summary contradict the source? (RAGAs faithfulness metric + manual spot-check)
2. **Determinism** — re-run 3× per leg; assert byte equality (V2) or N-of-M consistency (V1)
3. **Latency** — wall-clock per stage
4. **Cost** — Claude API tokens (V1) vs compute seconds (V2)
5. **Layout fidelity** — table/figure preservation (becomes critical for Comprehensive tier)

## TDD framing

Per `tdd-core/testing-tdd` and `python-dev/testing-python` plugins (declared in [`.claude/settings.json`](../.claude/settings.json)):

- **pytest** for known cases — Arrange-Act-Assert; naming `test_{module}_{component}_{behavior}`
- **Hypothesis** for property-based assertions on V1's nondeterministic stages — "extracted entities ⊇ {known minimum}", "schema validates", "key claims contain expected substrings"
- **inline-snapshot** for golden-output regression on V2's deterministic stages
- Schema gates already TDD'd in [roadmap §0.1.0 — Contracts](roadmap.md#010--contracts) (38 round-trip tests)

| Stage type | Tooling |
|---|---|
| Pure functions (V2 discover, normalize, render) | pytest + inline-snapshot |
| LLM stages (V1 extract, normalize, analyze, render) | pytest + Hypothesis property assertions |
| Parallel diff harness | pytest with mock pipelines |

## Sequencing

1. **V1 first** — fastest path to any working E2E loop. ~1–2 days. Builds on [roadmap §0.2.0 — Runner](roadmap.md#020--runner).
2. **V2 normalize + render only**, reusing V1 extraction output. Lets us A/B "Claude extract vs docling extract" cheaply by swapping one stage.
3. **Full V2** + parallel diff harness. Run the eval matrix.
4. Decide per stage: keep Claude, swap to tools, or run both as cross-validation (mirrors [roadmap §0.4.0 — Adapters](roadmap.md#040--adapters) cross-validation strategy).

PDF is the cleanest A/B — neither variant shares Office-format deps in extract. Office formats share `python-docx` / `openpyxl` / `python-pptx`, so the V1-vs-V2 signal there is weaker.

## Out of scope for v1

- Comprehensive tier (full canonical tree, RAG indexing, citations) — [roadmap §0.5.0 — Domain packs](roadmap.md#050--domain-packs)
- Source connectors beyond local filesystem — [roadmap §0.5.0 — Domain packs](roadmap.md#050--domain-packs)
- Domain packs — [roadmap §0.5.0 — Domain packs](roadmap.md#050--domain-packs)
- `OutputFormat` / `FormatConformance` strict validators — [roadmap §0.6.0 — Eval](roadmap.md#060--eval)
- Multi-sample evaluation — once v1 lands on one sample, expand sample set

## References

- [Architecture](architecture.md) — stage graph + contracts
- [Roadmap](roadmap.md) — milestone scope per version
- [landscape-ingest.md](landscape-ingest.md), [landscape-process.md](landscape-process.md), [landscape-output.md](landscape-output.md), [landscape-prior-art.md](landscape-prior-art.md) — tool surveys feeding this plan
