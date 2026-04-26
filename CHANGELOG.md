<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Added

- [§0.2.0 — Runner](docs/roadmap.md#020--runner) scaffold: `runner.py` (stage chain + gate validation, halt-on-first-failure with `PipelineError` carrying stage and contract names), `base/adapter.py` (`AdapterBase` ABC), and `stages/__init__.py`
- `stages/discover.py` — filesystem walk → `DiscoveryManifest` (sorted, sha256-hashed, glob-filtered)
- `stages/extract.py` — Kreuzberg-backed adapter → `ExtractionBundle`; deferred import so the module loads without the optional extra
- `pyproject.toml` `[project.optional-dependencies]` `extract` extra = `kreuzberg>=2.0` (MIT, local). Install with `uv sync --extra extract`
- `render/formats.py` — shared Markdown → DOCX + PDF utility (`render_artifacts`). Used by both V1 and V2 render stages so the A/B is purely about Markdown content. Pure-Python (markdown / python-docx / WeasyPrint), no JVM, no GPL.
- `pyproject.toml` `[project.optional-dependencies]` `render` extra = `markdown>=3.5`, `python-docx>=1.1`, `weasyprint>=62`. Install with `uv sync --extra render`
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
