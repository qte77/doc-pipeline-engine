# Prototype results

Outputs of the [parallel diff harness](prototype-plan.md) running both
V1 (Claude API) and V2 (Python tools) legs on the [prototype
samples](prototype-samples.md).

## Status

**Not yet populated.** The harness lands in PR 6; first real run requires
`uv sync --extra extract --extra render --extra v1 --extra v2-render`,
`ANTHROPIC_API_KEY` in env, and the samples downloaded via
`bash scripts/download-samples.sh --download`.

## Run procedure

```bash
# One sample
uv run python -m doc_pipeline_engine.harness samples/contracts/<file>.pdf \
  --output-dir outputs/

# Per-sample DiffReport JSON is emitted to stdout; rendered artifacts
# (md / docx / pdf for both legs) are written under outputs/<sha256>/.
```

## Eval axes (recap)

Per [prototype-plan.md → Eval axes](prototype-plan.md#eval-axes):

1. **Faithfulness** — V1 vs V2 summary contradicts source?
2. **Determinism** — re-run consistency
3. **Latency** — wall-clock per leg per stage
4. **Cost** — Claude API tokens (V1) vs compute seconds (V2)
5. **Layout fidelity** — table/figure preservation (matters for Comprehensive tier)

## Results — first run

*Pending.*

This file is updated by hand after the first end-to-end run on all
five prototype samples.
