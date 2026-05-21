<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Added

- `docs/landscape/process.md` §6 — schema-templated extraction landscape (NuExtract3 + outlines/instructor cross-refs). (#81)
- `external/` directory tree — off-the-shelf one-shot summarizers (Anthropic SDK + CC CLI + interactive doc) as comparison baseline. See [ADR-0004](docs/adr/0004-external-evaluators-vs-pipeline.md). (#61)
- `scripts/gen_contracts_md.py` + committed `docs/contracts.md` — auto-generated contracts reference consumed by external evaluators.
- `docs/adr/0004-external-evaluators-vs-pipeline.md` — records external-evaluators decision.
- `docs/roadmap.md` §0.2.3 — describes PR A (merged) + PR B + PR C (deferred CC SDK).
- New tests: `test_external_anthropic_sdk_run_oneshot`, `test_external_cc_cli_run_headless`, `test_gen_contracts_md` (3 each, RED-first).
- `python -m doc_pipeline_engine.models dump <Name>` CLI — emits `Model.model_json_schema()`.
- `tests/test_models_round_trip.py` — round-trip + negative-validation cases over all 10 models.
- `docs/adr/0001-pydantic-as-contract-source-of-truth.md` + `docs/roadmap.md` §0.2.1 entry.
- `mkdocs.yaml` + `.github/workflows/generate-deploy-mkdocs-ghpages.yaml` + `[dependency-groups] docs` extras + `make docs*` targets + [ADR-0002](docs/adr/0002-mkdocs-material-mkdocstrings-for-api-docs.md) + roadmap §0.2.2.
- `tests/test_stages_v2_normalize_headings.py` — five cases for v2 heading reconstruction.
- `docs/prototype/results/2026-04-26-run-3-v2-headings.md` — V2-only re-run after [#33](https://github.com/qte77/doc-pipeline-engine/issues/33).
- `stages/_v1_client.py` backend dispatch (explicit client → SDK → CLI → error) + `tests/test_v1_client_backend_dispatch.py`. Resolves [#30](https://github.com/qte77/doc-pipeline-engine/issues/30).
- `docs/prototype/results/2026-04-26-run-2-v1-cli.md` + `docs/prototype/results/README.md`.
- `.devcontainer/devcontainer.json` + Makefile bootstrap targets (`setup_uv`, `setup_dev`, `setup_claude_code`, `setup_npm_tools`, `setup_lychee`, `install_image_ocr`, `install_v2_nlp`). Resolves [#32](https://github.com/qte77/doc-pipeline-engine/issues/32).
- `.claude/rules/frontmatter-convention.md` + `.markdownlint.json` + plugin config. YAML frontmatter on `docs/landscape/*.md` and `docs/prototype/*.md`.
- `docs/prototype/results/2026-04-26-run-1-v2-only.md`.
- `.github/workflows/generate-sbom.yaml` + `write-llms-txt.yaml` + `.github/templates/llms.txt.tpl`.
- §0.2.0 Runner: `runner.py`, `base/adapter.py`, `stages/__init__.py`, `stages/discover.py`, `stages/extract.py`.
- `pyproject.toml` optional extras: `extract` (kreuzberg), `render` (markdown + python-docx + weasyprint), `anthropic_sdk` (anthropic), `local` / `local-render` / `local-eval`.
- `render/formats.py` — shared Markdown → DOCX + PDF utility.
- `anthropic_sdk` post-extraction stages: `normalize`, `analyze`, `render`, `eval` + `_anthropic_sdk_client.py`.
- `local` post-extraction stages: `normalize`, `analyze`, `render`, `eval` + Jinja template.
- Parallel diff harness `harness.py` — `run_both()` returns `DiffReport`.
- `docs/prototype/samples.md` + `docs/prototype/plan.md` (dual-variant E2E prototype plan).
- `Makefile` `test_rerun` / `test_fix_snapshots` / `validate` targets.
- `docs/landscape/process.md` + `output.md` + `e2e-systems.md` (originally `prior-art.md`, renamed in this cycle).

### Changed

- Rename `docs/landscape/prior-art.md` → `e2e-systems.md` (+ companion-link updates in three sibling landscape files + `mkdocs.yaml` nav + `README.md` + `CONTRIBUTING.md` + `docs/prototype/plan.md`) + GLM-OCR References URL fix in `ingest.md` (`zai-org/GLM-4` → `zai-org/GLM-OCR`). (#83)
- Enable Ruff `S` (bandit) and `C90` (mccabe, `max-complexity=10`); `tests/**` get `S101` ignore. Resolves #72; follow-up #75 tracks remaining rules. (#79)
- Migrate markdown linting from `markdownlint-cli` to `markdownlint-cli2` (single-file config in `.markdownlint-cli2.jsonc`).
- `docs/assets/architecture-bird.svg` redrawn with three lanes (anthropic_sdk + local + external evaluators side-panel).
- Pipeline legs renamed: `v1` → `anthropic_sdk`, `v2` → `local`. Output dirs, extras, Makefile targets, CLI flag, and stage filenames updated. Deprecated aliases ship for one cycle. See [ADR-0003](docs/adr/0003-rename-legs-anthropic-sdk-local.md).
- Pydantic v2 models replace the JSON-Schema gate as the contract source-of-truth. See [ADR-0001](docs/adr/0001-pydantic-as-contract-source-of-truth.md).
- `stages/local_normalize.py` (formerly `v2_normalize`) — flat heading tree via three regex families with 50% density-cap fallback. Resolves [#33](https://github.com/qte77/doc-pipeline-engine/issues/33).
- Reorganize docs into topical subdirs: `landscape-*.md` → `landscape/*.md`, `prototype-*.md` → `prototype/*.md`.
- `.claude/settings.json` enables `python-dev` and `commit-helper` plugins; `CONTRIBUTING.md` documents the plugin set.

### Removed

- CC-CLI fallback in `stages/_anthropic_sdk_client.py` (rolled back from #41/#30). Subscription-only users now run `external/cc_cli/run_headless.sh`. Three CLI-dispatch tests removed; explicit-client + SDK + no-API-key tests preserved.
- `contracts/` directory (10 hand-written JSON Schema files) — superseded by Pydantic models per [ADR-0001](docs/adr/0001-pydantic-as-contract-source-of-truth.md). `tests/test_contracts.py` and the `jsonschema` runtime dep gone with it.

### Fixed

- `anthropic_sdk` leg of the parallel-diff harness runs in subscription-only environments (claude CLI but no `ANTHROPIC_API_KEY`). Previously crashed at `_anthropic_sdk_client.make_client()`.
- `_anthropic_sdk_client._call_via_cli` passes the user prompt via stdin (was hitting argv length limit on the 220K-char contract DOCX).


## [0.1.0] - 2026-04-23

### Added

- 10 JSON contract schemas in `contracts/` (5 core, 5 reserved stubs)
- Gate validator (`src/doc_pipeline_engine/base/contracts.py`)
- Schema round-trip tests (38 tests)
- Sample download script with auto-generated manifest (~95 files)
- `docs/architecture.md` — stage graph, runner vs stream, package layout
- `docs/roadmap.md` — milestones 0.1.0–0.6.0 with reasoning
- `docs/scraping-landscape.md` — web scraping tool survey
- `.github/` PR and issue templates
- Apache-2.0 license with NOTICE for third-party sample content

### Changed

- Package layout: `workers/` → `src/doc_pipeline_engine/`
- Build system: setuptools → hatchling, pip → uv sync
- Makefile: MARK sections, auto-help, lint_md, lint_links
