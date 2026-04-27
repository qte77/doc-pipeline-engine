---
title: External one-shot evaluators
purpose: Off-the-shelf summarizers (Anthropic SDK, Claude Code CLI/SDK) compared against the in-process pipeline outputs
created: 2026-04-27
updated: 2026-04-27
validated_links: 2026-04-27
category: implementation
---

# README

External one-shot summarizers run **outside** the in-process
pipeline (`anthropic_sdk` and `local` legs in `src/`). Each runner
reads the raw sample bytes — no `Discover` / `Extract` /
`Normalize` / `Analyze` / `Render` / `Eval` — and produces a single
`summary.md` + `meta.json` per sample.

Their outputs are compared against the pipeline outputs in the
prototype results docs. See [ADR-0004](../docs/adr/0004-external-evaluators-vs-pipeline.md)
for the architectural decision.

## Variant matrix

|                    | Vanilla (no project context) | Project-augmented (.claude/) |
| ------------------ | ---------------------------- | ---------------------------- |
| Anthropic SDK      | `external/anthropic-vanilla` | `external/anthropic-project` |
| CC CLI (headless)  | `external/cc-cli-headless-vanilla` | `external/cc-cli-headless-project` |
| CC CLI (interactive) | — (user-driven; `cc-cli-interactive`) | (same; user follows project workflow) |
| CC SDK             | `external/cc-sdk-vanilla` (deferred) | `external/cc-sdk-project` (deferred) |

Vanilla = no `.claude/` skills/rules/plugins loaded. Project = full
`.claude/` autoloaded (CC) or `.claude/rules/*.md` hand-loaded
(Anthropic SDK, since the SDK has no native skills/plugins concept).

## Running

### Anthropic SDK

```bash
uv run python external/anthropic_sdk/run_oneshot.py \
  samples/legal/us/us-open-government-act-2007.pdf \
  --config vanilla \
  --output-dir outputs
```bash

Same with `--config project` for the augmented variant.

### CC CLI (headless)

```bash
bash external/cc_cli/run_headless.sh \
  samples/legal/us/us-open-government-act-2007.pdf \
  --config vanilla \
  --output-dir outputs
```

Vanilla mode invokes `claude --print --bare`; project mode runs
without `--bare`. Both are wrapped through `npx codeburn` for cost
capture (see [github.com/getagentseal/codeburn](https://github.com/getagentseal/codeburn)).

### CC CLI (interactive)

User-driven. See [`cc_cli/interactive.md`](cc_cli/interactive.md).

### CC SDK (deferred)

Lands in PR C — gated on `claude-agent-sdk` PyPI availability.

## Output layout

```text
outputs/<sample_sha256>/
  anthropic_sdk/                          # in-process pipeline reference
  local/                                  # in-process pipeline reference
  external/
    anthropic-{vanilla,project}/          summary.md  meta.json
    cc-cli-headless-{vanilla,project}/    summary.md  meta.json
    cc-cli-interactive/                   summary.md  meta.json   (user-dropped)
    cc-sdk-{vanilla,project}/             summary.md  meta.json   (deferred)
```bash

## Eval dimensions (run-4 prototype results)

Each variant is scored on six dimensions:

1. **Feasibility** — does the variant run on each sample?
2. **Usability** — invocation effort.
3. **Outcomes** — load-bearing facts present in the summary.
4. **Quality** — structural faithfulness, hallucination, format.
5. **Speed** — wall-time per sample.
6. **Locality / airgap** — `local` is `airgap-yes`; `anthropic_sdk` and
   external Anthropic SDK are `airgap-conditional` (when
   `ANTHROPIC_BASE_URL` points at a local LLM gateway); CC variants
   are `airgap-no`.

## Shared prompt + contracts reference

All runners use the same prompt at [`PROMPT.md`](PROMPT.md). The
runners also surface the pipeline's Pydantic contracts to the
external tool so its summary can structurally match the pipeline:

- **Anthropic SDK runners** inline [`docs/contracts.md`](../docs/contracts.md)
  into the system prompt (FIXME workaround — the SDK lacks
  native file-reading; ~5KB/request asymmetry tracked in the
  runner source).
- **CC runners** reference `docs/contracts.md` by path; the agent's
  Read tool fetches it on demand.

`docs/contracts.md` is auto-generated from the model registry by
`scripts/gen_contracts_md.py`; regenerate via `make docs_contracts`.
