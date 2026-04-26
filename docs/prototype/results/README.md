---
title: Prototype results — index
purpose: Index of harness runs across the five locked prototype samples
created: 2026-04-26
updated: 2026-04-26
validated_links: 2026-04-26
category: implementation
---

Each file under `docs/prototype/results/` is one harness run. Files are
dated and named after what changed since the previous run, so per-run
data accumulates without overwriting and trends are easy to read.

## Runs

| Date | File | Scope |
| --- | --- | --- |
| 2026-04-26 | [run 1 — V2 only](2026-04-26-run-1-v2-only.md) | First full harness run; V1 leg blocked by missing `ANTHROPIC_API_KEY`; diagram blocked by missing Tesseract. |
| 2026-04-26 | [run 2 — V1 + V2 (V1 via Claude Code CLI)](2026-04-26-run-2-v1-cli.md) | First fully-paired V1+V2 run. V1 dispatched via `claude` CLI fallback ([#41](https://github.com/qte77/doc-pipeline-engine/pull/41)); diagram extracted via Tesseract installed by `make install_image_ocr` ([#37](https://github.com/qte77/doc-pipeline-engine/pull/37)). |

## Sample roster

Locked in [../samples.md](../samples.md). Five samples covering one
use case each (contract / legal / invoice / spec / diagram) and a
representative file-type spread (DOCX + PDF + JPG).

## Conventions

- One file per run, named `YYYY-MM-DD-run-N-<short-tag>.md`.
- Each file stands alone — axes table, per-sample observations,
  faithfulness gaps, follow-ups. Don't refactor prior runs after the
  fact; they're snapshots.
- Raw `DiffReport` JSON and rendered artifacts go to `outputs/`
  (gitignored). Reference shas in the doc so artifacts stay
  traceable.
