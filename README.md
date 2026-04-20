# doc-pipeline-engine

Data plane for the `doc-pipeline` Claude Code plugin. Holds adapters (docling, GLM-OCR, PaddleOCR-VL, Claude CLI), stage contracts, domain packs, policies, and eval harnesses.

## Repo layout

```
contracts/      JSON schemas — the deterministic gate format between stages
workers/        Adapter implementations (stubs in v0.1, except claude_cli_adapter)
domains/        Domain packs (generic, mech-elec-cert, med-research-patents)
policies/       Data-locality policies (local-only, claude-api-extracted-only, cloud-redacted)
eval/           RAGAs / TruLens / DeepEval harnesses and orchestration-bench
tests/          pytest
samples/        Known-good sample inputs used by happy-path + failure tests
```

## v0.1 scope

- Contracts-first: the 10 JSON schemas in `contracts/` are the load-bearing design.
- Only the `generic` domain pack is fully wired; `mech-elec-cert` and `med-research-patents` are declared stubs.
- Only `claude_cli_adapter` is wired in v0.1; docling/GLM-OCR/PaddleOCR-VL are stubs.
- Happy-path test runs through stages Discover → Extract → RecognizeInputFormat → Normalize → Analyze → QuickDraft → Evaluate → Publish.
- Failure tests: F1 (corrupt PDF), F2 (adapter disagreement), F4 (schema drift), F5 (policy violation), F11 (format miss), F12 (required-section miss).

See `~/.claude/plans/doc-pipeline-engine-init.md` for the full v0.1 design doc.

## Quickstart

```bash
make install        # dev deps
make test-contracts # schema round-trip tests
make happy-path     # E2E on samples/generic/sample.pdf
make test-failure   # F1, F2, F4, F5, F11, F12
```

## Related

- Control-plane plugin: `/workspaces/qte77/claude-code-plugins/plugins/doc-pipeline/`
- Research landscape: `/workspaces/qte77/ai-agents-research/`
