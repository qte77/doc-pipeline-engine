<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

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
- `Makefile` `install-models` target — `uv run python -m spacy download en_core_web_sm` (needed for V2 NER).
- `CONTRIBUTING.md` documents the full extras taxonomy with locality flags.
- `Makefile` targets `test-rerun` (`pytest --lf -x`), `test-fix-snapshots` (`pytest --inline-snapshot=fix`), and `validate` (lint + test + lint-md + lint-links pre-commit gate)

### Added

- `docs/prototype-plan.md` — dual-variant E2E prototype plan (Claude Code vs landscape tools), Quick-tier-only, with TDD framing per `tdd-core` / `python-dev` plugins and a parallel-diff harness sketch. Roadmap §0.2.0, CONTRIBUTING doc hierarchy, and the four landscape files cross-link to it.

### Changed

- `.claude/settings.json` enables `python-dev` and `commit-helper` plugins from the `qte77-claude-code-utils` marketplace; `CONTRIBUTING.md` documents the plugin set under Setup

### Added

- `docs/landscape-process.md` — process-stage survey (chunking, table/figure extraction, NER, RAG indexing, CanonicalDoc normalization)
- `docs/landscape-output.md` — output-stage survey (rendering, office formats, templating, FormatConformance validators)
- `docs/landscape-prior-art.md` — E2E pipeline prior art (arXiv 2025 surveys, OSS systems, commercial IDP) and USP gap analysis

### Changed

- `docs/landscape.md` → `docs/landscape-ingest.md`; expanded with source connectors (SharePoint, Confluence, Drive, S3, IMAP, Exchange) and crawling/discovery sections (polyfetch-scrape, trafilatura, httpx, pathlib, watchdog)
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
- Makefile: MARK sections, auto-help, lint-md, lint-links
