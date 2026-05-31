---
title: ADR-0004 — External evaluators vs the in-process pipeline
purpose: Records the decision to ship Anthropic SDK + Claude Code one-shot summarizers as external evaluators in `external/` rather than as in-process pipeline legs
created: 2026-04-27
updated: 2026-05-25
validated_links: 2026-05-25
category: technical
---

## Status

Accepted — 2026-04-27

## Context and Problem Statement

The in-process pipeline ships two stage-decomposed legs (`anthropic_sdk`
and `local`, both in `src/doc_pipeline_engine/stages/`). Each leg goes
through `Discover → Extract → Normalize → Analyze → Render → Eval`.

The prototype goal is to A/B-compare the pipeline's output against
**off-the-shelf one-shot summarizers** — what a user would get from
sending a single LLM call instead of running a structured pipeline.
Two such summarizers matter:

- **Anthropic SDK called once** — single `client.messages.create(...)`,
  text in, markdown out. No `CanonicalDoc` / `AnalysisReport` / stages.
- **Claude Code** invoked off-the-shelf via the CLI (headless or
  interactive) or the Claude Agent SDK — the way a user would actually
  use Claude Code, not as a transport hijacked inside V1 stages.

Each summarizer has **two configurations**:

- **Vanilla** — no project context loaded.
- **Project-augmented** — `.claude/skills/`, `.claude/rules/`,
  `.claude/settings.json` plugins loaded.

Total external variants: 2 (Anthropic) + 6 (CC: 3 modes × 2 configs)
= 8.

Previous attempt (#41 / #30): the Claude Code CLI was wedged into V1's
`_v1_client.py` as a transport fallback for subscription-only users.
That conflated two different concerns — V1's transport (Anthropic SDK)
and CC's role as an external benchmark. It also made every CLI run
execute four Claude calls (one per stage) instead of one off-the-shelf
call, defeating the "off-the-shelf" intent.

## Decision Drivers

- Off-the-shelf one-shot summarizers must not run through pipeline stages — wedging CC-CLI into V1 executed 4 calls per sample and conflated transport with benchmarking
- External evaluators receive the raw sample file to preserve off-the-shelf realism, including each tool's own extraction quality
- The 2×2×3 variant matrix (Anthropic + CC × vanilla/project × headless/interactive/agent-sdk) must not force a Stage shape onto one-shot tools

## Considered Options

### Option 1 — External `external/` directory with standalone runners

- Good, because no pipeline stages imposed on one-shot tools; each runner is a few lines
- Good, because off-the-shelf realism preserved: external evaluators process the raw sample file including their own extraction
- Good, because CC's native PDF-reading capability remains part of the test; extraction-quality differences are surfaced
- Good, because subscription-only users have a clear path via `external/cc_cli/run_headless.sh`
- Bad, because cost axis is asymmetric across variants (SDK per-call from envelope, CC per-session via codeburn, `local` is free)
- Bad, because subscription-only users no longer have a V1 path; behavior change vs pre-#54 main

### Option 2 — CC-CLI as transport fallback inside V1 stages (rolled-back #41 design)

- Good, because single code path for all LLM-backed runs; existing V1 call sites work for CC users without separate scripts
- Bad, because runs 4 Claude calls per sample (one per stage), conflating external comparison with V1's transport choice
- Bad, because defeats off-the-shelf intent: a real user sends one call, not four

### Option 3 — Third in-process leg in `harness.py`

- Good, because unified harness runs all legs; results land in the same report structure
- Bad, because forces a Stage shape onto one-shot tools; tests would have to invent fake `Discover` / `Extract` outputs for a leg that doesn't go through them

### Option 4 — Share `Extract` output with external evaluators (apples-to-apples on summarization quality alone)

- Good, because isolates summarization quality from extraction quality; fairer comparison of the LLM reasoning step
- Bad, because loses CC's native PDF-reading capability from the test
- Bad, because hides extraction-quality differences, which are part of what the prototype measures

## Decision Outcome

Chosen: **Option 1 — External `external/` directory with standalone runners**.
External one-shot summarizers live in **`external/`** as standalone
runners, **not** as in-process pipeline stages. Their outputs land in
`outputs/<sha>/external/<variant>/` and are compared against the
pipeline outputs in the prototype results docs (run-4 onward).

No external evaluator runs through `harness.py` or any
`stages/*.py`. The CC-CLI fallback in `_anthropic_sdk_client.py` is
**removed** (rolling back the relevant part of #41); subscription-only
users now run `external/cc_cli/run_headless.sh` instead.

External evaluators receive the **raw sample file**, not Kreuzberg's
extracted text. Off-the-shelf realism wins over apples-to-apples
uniformity. The comparison gains a documented asymmetry: external
tool quality includes its own extraction; pipeline quality includes
Kreuzberg's. Off-the-shelf is what we want to measure.

### Vanilla / project asymmetry per transport

For the Anthropic SDK runner:

- **Vanilla** is the natural state — the SDK has no project awareness.
- **Project** is *simulated* by hand-loading `.claude/rules/*.md` into
  the system prompt. The SDK has no native skills/plugins concept;
  this answers "if a user pasted the project's rule files into their
  system prompt, would the output improve?"

For the CC CLI runner:

- **Vanilla** uses `claude --print --bare` — `--bare` suppresses
  project-context auto-discovery cleanly.
- **Project** runs from repo root; `.claude/{skills,rules,settings.json}`
  auto-load. This is Claude Code's natural behavior in this repo.

The asymmetry is informational: it documents that CC's "off-the-shelf"
usage already includes project conventions when present, while the
SDK's "off-the-shelf" usage does not.

### Contracts reference for external tools

External summarizers see the pipeline's Pydantic contracts via
`docs/contracts.md` (auto-generated by `scripts/gen_contracts_md.py`)
so their summaries can structurally match the pipeline output:

- **Anthropic SDK runners** **inline** `docs/contracts.md` into the
  system prompt. **FIXME(sdk-no-file-reading)**: the SDK lacks a
  native Read tool; ~5KB/request asymmetry vs CC. Switch to
  reference-only when the SDK gains a Read-equivalent tool or when
  we wrap it with one.
- **CC runners** **reference** `docs/contracts.md` by file path; the
  agent's Read tool fetches it on demand.

### Cost capture (asymmetric by transport)

- Anthropic SDK variants: cost computed from `response.usage` (input/
  output tokens × Anthropic Opus 4.x pricing).
- CC variants: cost captured via [`npx codeburn`](https://github.com/getagentseal/codeburn) —
  a cost-monitoring wrapper for Claude Code. The runner pipes `claude`
  output through codeburn; codeburn emits `CODEBURN_COST_USD=<float>`
  on stderr; the runner writes that to `meta.json.cost_usd`.

## Consequences

- Subscription-only users no longer have an `anthropic_sdk` in-process
  path; they use `external/cc_cli/run_headless.sh` instead. Behavior
  change vs pre-#54 main.
- Cost axis is asymmetric (`anthropic_sdk` reports per-call from SDK
  envelope, `local` is free, external CC variants report per-session
  via codeburn, external Anthropic variants report per-call). Apples-to-apples cost
  view is a §0.6.0 Eval concern; for run-4 we surface the differences
  honestly and let the reader normalize.
- The 2×2×3 variant matrix is large but each cell is a few lines;
  complexity lives in the eval/results doc, not the runners.
- `docs/contracts.md` becomes a load-bearing artifact — external
  evaluators read it to match pipeline structure. Drift between the
  models and the file fails CI via `make docs_contracts` (idempotent
  generator).
- Eval dimensions widen from latency/cost (run-2) to six axes:
  feasibility, usability, outcomes, quality, speed, and locality
  (airgap-yes / airgap-conditional / airgap-no). The `local` pipeline
  is the only `airgap-yes` variant.

## More Information

- [github.com/getagentseal/codeburn](https://github.com/getagentseal/codeburn)
  — cost-monitoring wrapper for Claude Code.
- [`external/README.md`](../../external/README.md) — runner-by-runner
  invocation guide.
- [`external/cc_cli/interactive.md`](../../external/cc_cli/interactive.md)
  — user-driven workflow for the CC interactive variant.
- [`scripts/gen_contracts_md.py`](../../scripts/gen_contracts_md.py)
  — generator for the contracts reference.
