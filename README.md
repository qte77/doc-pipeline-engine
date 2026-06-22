# doc-pipeline-engine

[![License](https://img.shields.io/badge/license-Apache_2.0-58f4c2.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-0.1.0-58f4c2.svg)
[![CodeQL](https://github.com/qte77/doc-pipeline-engine/actions/workflows/codeql.yaml/badge.svg)](https://github.com/qte77/doc-pipeline-engine/actions/workflows/codeql.yaml)
[![CodeFactor](https://www.codefactor.io/repository/github/qte77/doc-pipeline-engine/badge)](https://www.codefactor.io/repository/github/qte77/doc-pipeline-engine)

Modular document processing engine with contract-gated pipeline stages. Standalone module — usable independently or as a component in larger systems (e.g. polyforge, office-polyforge).

## Quickstart

```bash
make install        # uv sync
make test_contracts # schema round-trip tests
```

## Run

Offline `local` leg — no API key, no cloud:

```bash
make run_local SAMPLE=samples/legal/us/us-open-government-act-2007.pdf
```

Full run surface (both legs, CLI switches, `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL`) → [CONTRIBUTING.md § Running the pipeline](CONTRIBUTING.md#running-the-pipeline).

## Devcontainer

Reproducible dev env at `.devcontainer/devcontainer.json` (Python 3.13 + Claude Code + lint tooling). Optional system deps install on demand per use case:

- `make install_image_ocr` — Tesseract for image-sample extraction
- `make install_local_nlp` — spaCy `en_core_web_sm` for `local`-leg NER entities

`anthropic_sdk` stages work with `ANTHROPIC_API_KEY` set (uses the
Anthropic SDK). Subscription-only users run `external/cc_cli/run_headless.sh`
instead — see [ADR-0004](docs/adr/0004-external-evaluators-vs-pipeline.md).

## Docs

- [Architecture](docs/architecture.md) — stage graph, runner vs stream, package layout
- [Roadmap](docs/roadmap.md) — milestones with reasoning and implementation notes
- Landscape — pipeline tool surveys: [ingest](docs/landscape/ingest.md), [process](docs/landscape/process.md), [output](docs/landscape/output.md), [E2E systems](docs/landscape/e2e-systems.md), [domain extraction](docs/landscape/domain-extraction.md)
- [Scraping Landscape](https://github.com/qte77/polyfetch-scrape/blob/main/docs/scraping-landscape.md) — web scraping survey (moved to `polyfetch-scrape`)
- [Changelog](CHANGELOG.md) — release history ([semver](https://semver.org/))
