<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

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
- `docs/prototype/results.md` — first-run results of the parallel diff harness on the five locked prototype samples (V2-only; V1 leg blocked pending [#30](https://github.com/qte77/doc-pipeline-engine/issues/30))

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
