---
title: CC CLI interactive workflow
purpose: User-driven Claude Code TUI session that drops a comparable summary into outputs/<sha>/external/cc-cli-interactive/
created: 2026-04-27
updated: 2026-04-27
validated_links: 2026-04-27
category: implementation
---

The headless variant ([`run_headless.sh`](run_headless.sh)) covers
automated comparison. The interactive variant covers **how a user
actually uses Claude Code on a document** — one TUI session, full
toolset, free-form back-and-forth.

This file is **manual workflow** — no automation. The user runs
Claude Code interactively, then drops the resulting summary into
the agreed output dir so it can sit alongside the headless +
Anthropic + pipeline outputs in the run-4 results doc.

## When to use this variant

- Tests CC's *interactive capability*, including any back-and-forth
  the user does with the model (asking clarifying questions,
  pasting more context, iterating on the summary shape).
- Provides a baseline against the headless / SDK variants so we can
  see whether interactive use moves the needle on summary quality.

## Workflow

1. **Compute the sample's sha256** (matches the other variants'
   output dir naming). Easiest:

   ```bash
   sha256sum samples/legal/us/us-open-government-act-2007.pdf | awk '{print $1}'
   ```

2. **Open Claude Code** in this repo:

   ```bash
   cd /workspaces/qte77/doc-pipeline-engine
   claude
   ```

3. **Read the shared prompt + contracts**: in the TUI session, ask
   Claude Code to read [`external/PROMPT.md`](../PROMPT.md) and
   [`docs/contracts.md`](../../docs/contracts.md). Then point it at
   the sample:

   ```text
   read external/PROMPT.md
   read docs/contracts.md
   read samples/legal/us/us-open-government-act-2007.pdf
   produce a summary following the prompt structure
   ```

   Iterate as a real user would — asking follow-ups, requesting
   reformatting, cross-checking a claim.

4. **Capture the cost** at session end:

   ```text
   /cost
   ```

   Note the `total_cost_usd` value.

5. **Drop the summary** into the output dir:

   ```bash
   SHA=<the sha256 from step 1>
   DIR=outputs/$SHA/external/cc-cli-interactive
   mkdir -p "$DIR"
   # paste the final summary into $DIR/summary.md
   ```

6. **Write `meta.json`** with the same shape as the other variants:

   ```bash
   cat > "$DIR/meta.json" <<EOF
   {
     "variant": "cc-cli-interactive",
     "transport": "cc-cli",
     "config": "interactive",
     "model": "claude-opus-4-7",
     "wall_seconds": <session minutes × 60>,
     "cost_usd": <from /cost>,
     "input_tokens": <from /cost or claude --debug>,
     "output_tokens": <from /cost or claude --debug>,
     "notes": "<optional: any back-and-forth observations>"
   }
   EOF
   ```

   Wall time is approximate (session length); cost comes from `/cost`
   inside the TUI. The `notes` field captures qualitative
   observations the headless run can't surface (e.g. "needed two
   reformat requests before the markdown matched the prompt
   structure").

## What to expect in the run-4 results doc

The interactive cell goes in the same axes table as the other
variants but with a `notes` column highlighting the qualitative
observations. For dimensions where the interactive cell is hard
to score (speed, since session length varies with user pace), the
results doc reports the headless figures as the reproducible
baseline.
