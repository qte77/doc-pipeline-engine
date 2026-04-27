<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Changed

- Pydantic v2 models replace the JSON-Schema gate as the single source of truth for stage contracts. `src/doc_pipeline_engine/models/` ships one `BaseModel` per contract (10 total) with a `REGISTRY` mapping. `base/contracts.py` rewritten as a thin Pydantic-backed wrapper — public API (`validate`, `is_valid`) unchanged, internally dispatches into `Model.model_validate(...)` and raises `ContractValidationError`. `runner.py` raises `PipelineError` from `ContractValidationError` (no longer depends on `jsonschema`). Resolves the typed-contract goal of [§0.2.1](docs/roadmap.md#021--typed-contracts); see [ADR-0001](docs/adr/0001-pydantic-as-contract-source-of-truth.md).

### Added

- `python -m doc_pipeline_engine.models dump <Name>` CLI — emits `Model.model_json_schema()` for any consumer that needs the JSON Schema view; replaces the deleted `contracts/*.schema.json` files.
- `tests/test_models_round_trip.py` — round-trip + negative-validation cases over all 10 models (replaces `tests/test_contracts.py`).
- `docs/adr/0001-pydantic-as-contract-source-of-truth.md` — records the decision and rejected alternatives.
- `docs/roadmap.md` §0.2.1 entry.

### Removed

- `contracts/` directory (10 hand-written JSON Schema files) — superseded by Pydantic models per ADR-0001.
- `tests/test_contracts.py` — superseded by the two new model test files.
- `jsonschema` runtime dependency in `pyproject.toml`.

### Changed

- `stages/v2_normalize.py` — reconstructs a flat heading tree from Kreuzberg's plain text via three regex families (formal-prefix `SECTION`/`SEC.`/`CHAPTER`/`ARTICLE`/`PART`, numbered `5.1 Title`, glued numbered `1Title`). Each detected heading becomes one section node carrying `title` + body text; falls back to single-leaf on zero headings or detected density >50% of non-empty lines. Resolves [#33](https://github.com/qte77/doc-pipeline-engine/issues/33): V2 now produces N claims per document instead of one, matching V1's structural granularity. `v2_analyze` / `v2_render` / `v2_eval` untouched.

### Added

- `tests/test_stages_v2_normalize_headings.py` — five cases covering numbered-with-space, formal-prefix, numbered-glued splitting, density-cap fallback, and zero-heading fallback. All gated on `is_valid("CanonicalDoc", …)`.
- `docs/prototype/results/2026-04-26-run-3-v2-headings.md` — V2-only re-run on the five locked samples after #33; legal goes 1 → 22 claims, spec 1 → 98; invoice/diagram correctly stay at 1.

### Added

- `stages/_v1_client.py` backend dispatch — explicit injected client → Anthropic SDK with `ANTHROPIC_API_KEY` → `claude` CLI on PATH (uses Claude subscription auth) → clear error. Resolves [#30](https://github.com/qte77/doc-pipeline-engine/issues/30) so V1 stages run in environments without a cloud API key.
- `tests/test_v1_client_backend_dispatch.py` — six unit tests covering precedence, both happy paths (SDK / CLI), the `is_error` propagation, and the no-backend RuntimeError.

### Fixed

- V1 leg of the parallel diff harness now runs in subscription-only environments (codespaces with `claude` CLI but no `ANTHROPIC_API_KEY`). Previously crashed at `_v1_client.make_client()`.
- `_v1_client._call_via_cli` passes the user prompt via stdin instead of as a positional argv. Argv path raised `OSError: [Errno 7] Argument list too long` on the contract DOCX (220K chars of extracted text). Caught by the run-2 multi-sample E2E.

### Added

- `docs/prototype/results/2026-04-26-run-2-v1-cli.md` — first fully-paired V1+V2 harness run on all five locked samples; V1 dispatched via the `claude` CLI fallback. Includes per-sample axes, content-delta example, and faithfulness gaps surfaced by the run.
- `docs/prototype/results/README.md` — index of harness runs (one file per run, dated).

### Added

- `.devcontainer/devcontainer.json` — minimal reproducible Codespaces / VS Code dev container (Python 3.13 + Claude Code + ruff/markdownlint/lychee). `onCreateCommand` runs `make setup_uv`; `postCreateCommand` runs `make setup_dev`. Pattern lifted from `qte77/Agents-eval`.
- `Makefile` `setup_uv`, `setup_dev`, `setup_claude_code`, `setup_npm_tools`, `setup_lychee` targets — wire the devcontainer's bootstrap chain (frozen `uv sync`, then full dev tooling via subtargets).
- `Makefile` `install_image_ocr` — use-case-named on-demand install of `tesseract-ocr` + `tesseract-ocr-eng`. Resolves [#32](https://github.com/qte77/doc-pipeline-engine/issues/32) so the prototype harness can extract image samples (`samples/mech-elec-cert/wikimedia-arduino-uno-r3.jpg`) without OCRError.
- `Makefile` `install_v2_nlp` — use-case-named on-demand install grouping `--extra v2` + `python -m spacy download en_core_web_sm` for V2 NER entities.

### Changed

- `Makefile` `install_models` — kept as a one-line alias for `install_v2_nlp` for one release cycle; removal queued for §0.5.0. Naming convention going forward: `install_<use_case>` (snake_case, each target installs the apt package + Python extra + model needed for one capability, in one command).

### Added

- `.claude/rules/frontmatter-convention.md` — exact import of `qte77-claude-code-utils/docs-governance/rules/frontmatter-convention.md`; enforces YAML frontmatter (`title`, `purpose`, `created`, `updated`, `validated_links`) on `**/*.md` outside the exempt set
- `.markdownlint.json` — `MD013: false` (line length) and `MD041.front_matter_title` per the imported rule, so frontmatter `title:` satisfies the first-heading check
- `.claude/settings.json` `enabledPlugins` — `docs-governance@qte77-claude-code-utils`
- YAML frontmatter on all `docs/landscape/*.md` and `docs/prototype/*.md` files; body H1 dropped (frontmatter `title` represents it per the rule)
- `docs/prototype/results/2026-04-26-run-1-v2-only.md` — first-run results of the parallel diff harness on the five locked prototype samples (V2-only; V1 leg blocked pending [#30](https://github.com/qte77/doc-pipeline-engine/issues/30)). Originally landed as `docs/prototype/results.md`; relocated under `results/` so per-run files accumulate without overwriting.

### Changed

- Reorganized docs into topical subdirs: `docs/landscape-*.md` → `docs/landscape/*.md` (drops the redundant `landscape-` prefix), `docs/prototype-*.md` → `docs/prototype/*.md`. All cross-references in `CHANGELOG.md`, `CONTRIBUTING.md`, `README.md`, `docs/roadmap.md`, `docs/llms.txt`, `.github/templates/llms.txt.tpl`, and intra-doc links were updated.
- `.gitignore` — ignore `outputs/` (harness-generated artifacts: per-sample md/docx/pdf and `v2_summary.json`)
- `Makefile` — drop redundant `@` prefixes and backslash continuations in the `help` recipe (`.SILENT` and `.ONESHELL` already declared); ignore `outputs/**` in `markdownlint`

### Added

- `.github/workflows/generate-sbom.yaml` — calls `qte77/gha-sbom-action@v0.1.0` on weekly cron + push-to-main; outputs SPDX SBOM to `docs/SBOM/`
- `.github/workflows/write-llms-txt.yaml` — calls `qte77/gha-llms-txt-action@v0.1.0`; auto-generates `docs/llms.txt` from `.github/templates/llms.txt.tpl` whenever docs/src/governance change
- `.github/templates/llms.txt.tpl` — llms.txt index template covering architecture, roadmap, prototype-plan, four landscape docs, and governance files

### Added

- [§0.2.0 — Runner](docs/roadmap.md#020--runner) scaffold: `runner.py` (stage chain + gate validation, halt-on-first-failure with `PipelineError` carrying stage and contract names), `base/adapter.py` (`AdapterBase` ABC), and `stages/__init__.py`
- `stages/discover.py` — filesystem walk → `DiscoveryManifest` (sorted, sha256-hashed, glob-filtered)
- `stages/extract.py` — Kreuzberg-backed adapter → `ExtractionBundle`; deferred import so the module loads without the optional extra
- `pyproject.toml` `[project.optional-dependencies]` `extract` extra = `kreuzberg>=2.0` (MIT, local). Install with `uv sync --extra extract`
- `render/formats.py` — shared Markdown → DOCX + PDF utility (`render_artifacts`). Used by both V1 and V2 render stages so the A/B is purely about Markdown content. Pure-Python (markdown / python-docx / WeasyPrint), no JVM, no GPL.
- `pyproject.toml` `[project.optional-dependencies]` `render` extra = `markdown>=3.5`, `python-docx>=1.1`, `weasyprint>=62`. Install with `uv sync --extra render`
- V1 (Claude API) post-extraction stages: `stages/v1_normalize.py` (ExtractionBundle → CanonicalDoc), `stages/v1_analyze.py` (CanonicalDoc → AnalysisReport), `stages/v1_render.py` (AnalysisReport → RenderArtifacts via shared `render_artifacts`), `stages/v1_eval.py` (minimal pass-through EvalReport). Shared Anthropic helper at `stages/_v1_client.py` with deferred import + dependency-injectable `client` parameter for stub-based testing. Default model `claude-opus-4-7`.
- `pyproject.toml` `[project.optional-dependencies]` `v1` extra = `anthropic>=0.40`. Install with `uv sync --extra v1`. V1 stages skipped in CI; integration smoke runs locally with `ANTHROPIC_API_KEY`.
- V2 (deterministic Python tools) post-extraction stages: `stages/v2_normalize.py` (ExtractionBundle → CanonicalDoc), `stages/v2_analyze.py` (claims via heading-walk; entities via spaCy NER when available, empty otherwise), `stages/v2_render.py` (Jinja2 template → Markdown → `render_artifacts`), `stages/v2_eval.py` (minimal pass-through EvalReport). Jinja template at `stages/_jinja_templates/quick_summary.md.j2` packaged by hatchling.
- `pyproject.toml` `[project.optional-dependencies]` `v2 = [jinja2, spacy]`, `v2-render = [jinja2]` (subset for Python 3.14 envs without spaCy wheels), `v2-eval = [deepeval]` (wired by PR 6 harness).
- `Makefile` `install_models` target — `uv run python -m spacy download en_core_web_sm` (needed for V2 NER).
- `CONTRIBUTING.md` documents the full extras taxonomy with locality flags.
- Parallel diff harness — `harness.py` with `run_both(sample_path, ...)` returning a `DiffReport` (`LegResult` per variant: contracts, RenderArtifacts, wall_times, eval_report). Extraction is shared (Kreuzberg runs once); only post-extraction stages diverge per leg. CLI: `python -m doc_pipeline_engine.harness <sample> [--output-dir DIR]`. Renders md/docx/pdf to `outputs/<sha256>/v1/` and `outputs/<sha256>/v2/`.
- `docs/prototype/samples.md` — selection criteria for the five prototype samples (one per use case: bidtender / legal / invoice / spec / diagrams).
- `docs/prototype/results.md` — placeholder for first-run eval results across the five eval axes (faithfulness, determinism, latency, cost, layout fidelity).
- `Makefile` targets `test_rerun` (`pytest --lf -x`), `test_fix_snapshots` (`pytest --inline-snapshot=fix`), and `validate` (lint + test + lint_md + lint_links pre-commit gate)

### Added

- `docs/prototype/plan.md` — dual-variant E2E prototype plan (Claude Code vs landscape tools), Quick-tier-only, with TDD framing per `tdd-core` / `python-dev` plugins and a parallel-diff harness sketch. Roadmap §0.2.0, CONTRIBUTING doc hierarchy, and the four landscape files cross-link to it.

### Changed

- `.claude/settings.json` enables `python-dev` and `commit-helper` plugins from the `qte77-claude-code-utils` marketplace; `CONTRIBUTING.md` documents the plugin set under Setup

### Added

- `docs/landscape/process.md` — process-stage survey (chunking, table/figure extraction, NER, RAG indexing, CanonicalDoc normalization)
- `docs/landscape/output.md` — output-stage survey (rendering, office formats, templating, FormatConformance validators)
- `docs/landscape/prior-art.md` — E2E pipeline prior art (arXiv 2025 surveys, OSS systems, commercial IDP) and USP gap analysis

### Changed

- `docs/landscape.md` → `docs/landscape/ingest.md`; expanded with source connectors (SharePoint, Confluence, Drive, S3, IMAP, Exchange) and crawling/discovery sections (polyfetch-scrape, trafilatura, httpx, pathlib, watchdog)
- `CONTRIBUTING.md` documentation hierarchy updated to reference the four landscape files

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
