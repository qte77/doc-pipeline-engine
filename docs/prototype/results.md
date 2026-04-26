# Prototype results

Outputs of the [parallel diff harness](plan.md) running both
V1 (Claude API) and V2 (Python tools) legs on the [prototype
samples](samples.md).

## Status

**First run completed 2026-04-26 — V2 leg only.** V1 leg blocked pending
[#30](https://github.com/qte77/doc-pipeline-engine/issues/30): the
codespace this run executed in had no `ANTHROPIC_API_KEY`. Issue #30
proposes a Claude Code headless-mode fallback so future runs work on any
host where `claude` is on `PATH`.

## Run procedure

```bash
uv sync --extra extract --extra render --extra v1 --extra v2-render
bash scripts/download-samples.sh --download
uv run python -m doc_pipeline_engine.harness <sample> --output-dir outputs/
```

The first run used a one-shot V2-only driver (V1 path blocked); future
runs use the harness CLI directly.

## Samples (locked)

| Use case | Path | sha256 (head) | Bytes |
| --- | --- | --- | --- |
| Contract | `samples/contracts/uk-short-form-contract.docx` | `88c177fe3a74` | 292,704 |
| Legal | `samples/legal/us/us-open-government-act-2007.pdf` | `3af32df1de87` | 136,565 |
| Invoice | `samples/invoices/nifc-sf1034-invoice.pdf` | `bedf3200fa3c` | 112,565 |
| Spec | `samples/mech-elec-cert/ti-ne555-datasheet.pdf` | `1df8d26a8bd7` | 2,259,992 |
| Diagram | `samples/mech-elec-cert/wikimedia-arduino-uno-r3.jpg` | _(extract failed)_ | 244,070 |

## V2 axes (first run)

| Sample | Extract chars | V2 wall (s) | Claims | Entities | Verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| Contract (DOCX) | 219,840 | 0.92 | 1 | 0 | pass |
| Legal (PDF) | 21,818 | 0.14 | 1 | 0 | pass |
| Invoice (PDF) | 5,228 | 0.12 | 1 | 0 | pass |
| Spec (PDF) | 57,174 | 0.39 | 1 | 0 | pass |
| Diagram (JPG) | — | — | — | — | error |

V2 wall time decomposes as roughly 80–95 % extract + render, and < 1 %
each for normalize/analyze/eval. Per-sample raw JSON in
`outputs/v2_summary.json`; rendered Markdown / DOCX / PDF in
`outputs/<sha256>/v2/`.

## Faithfulness gaps and surprises

1. **`claims = 1` across every sample.** `v2_normalize` builds a single
   leaf containing the whole extracted text, so `v2_analyze`'s
   heading-walk produces exactly one claim — the first sentence of the
   document. The "first sentence" heuristic boundary is `.!?`, which:
   - works for the legal sample (`PUBLIC LAW 110–175—DEC.`) and the
     invoice (`Standard Form 1034 VOUCHER NO.`),
   - degenerates on the UK contract DOCX into a ~3.6 KB bullet
     containing the entire table-of-contents (no `.!?` until well past
     the ToC),
   - clips the NE555 datasheet feature list at the first period, losing
     the body.
   None of these are schema violations — `AnalysisReport.claims` only
   requires `minItems=1` — but they show that V2 normalize is the place
   to add real heading-tree reconstruction (Kreuzberg returns flat text;
   the structure has to be inferred). Tracked toward §0.5.0.

2. **`entities = 0` everywhere.** Expected: this run used `--extra
   v2-render` (no spaCy) because the codespace is on Python 3.14 and
   spaCy lacks 3.14 wheels. `_maybe_extract_entities` returns `[]`
   silently when spaCy is missing; the report stays schema-valid. To
   exercise the NER path, switch to a Python 3.13 codespace and `uv
   sync --extra v2`.

3. **Image extraction blocked.** Kreuzberg's image path requires a
   Tesseract install with `eng.traineddata`; this codespace has neither.
   The diagram sample failed at `extract` with
   `OCRError: Failed to initialize language 'eng'`. Two fixes possible:
   add a devcontainer post-create step that installs `tesseract-ocr +
   tesseract-ocr-eng`, or document the requirement in the run procedure.
   Filed as a follow-up rather than blocking the prototype.

4. **Render is single-bullet Markdown by design.** `v2_render` Jinja
   template emits `# Quick Summary\n## Key Claims\n- {claim}\n` for
   each claim. With one claim per doc, the rendered MD/DOCX/PDF are
   small (legal: 59 chars MD → 6.5 KB PDF). Once V2 normalize starts
   producing real sections, render will fan out automatically —
   template doesn't need changes.

5. **Eval is shallow but honest.** `v2_eval` only checks
   `schema_valid`. Faithfulness, determinism, latency, cost axes are
   not yet wired into the eval report itself; they live in the diff
   harness's `axes` dict. With V1 unavailable, the comparative axes
   (`latency_ratio_v1_over_v2`, `faithfulness_delta`, `cost_tokens`)
   couldn't be computed this run.

## Open follow-ups (from this run)

- **#30 — Claude Code headless fallback for V1.** Required to A/B at
  all without a paid API key. _Implementation queued in next session._
- **Tesseract devcontainer step** — image samples can't extract until
  this lands; affects the diagram leg of the A/B.
- **V2 normalize: heading-tree reconstruction** — the single-leaf
  shortcut produces structurally honest but semantically empty
  AnalysisReports. Worth landing before §0.5.0 Comprehensive tier.
- **Re-run on Python 3.13 codespace** for spaCy NER coverage, or wait
  for spaCy 3.14 wheels.
