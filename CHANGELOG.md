<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

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
