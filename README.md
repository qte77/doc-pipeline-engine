# doc-pipeline-engine

[![License](https://img.shields.io/badge/license-Apache_2.0-58f4c2.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-0.1.0-58f4c2.svg)
[![CodeQL](https://github.com/qte77/doc-pipeline-engine/actions/workflows/codeql.yaml/badge.svg)](https://github.com/qte77/doc-pipeline-engine/actions/workflows/codeql.yaml)
[![CodeFactor](https://www.codefactor.io/repository/github/qte77/doc-pipeline-engine/badge)](https://www.codefactor.io/repository/github/qte77/doc-pipeline-engine)

Modular document processing engine with contract-gated pipeline stages. Standalone module — usable independently or as a component in larger systems (e.g. polyforge, office-polyforge).

## What

- Turns documents (PDF / Office / images / email / text) into structured summaries through contract-gated pipeline stages.
- Two interchangeable legs: `local` (offline, no API key — spaCy + Jinja) and `anthropic_sdk` (cloud LLM, vendor-configurable via `base_url` for Bedrock / Vertex / gateways).
- Every stage boundary is validated against Pydantic v2 contracts ([ADR-0001](docs/adr/0001-pydantic-as-contract-source-of-truth.md)).
- Renders results to Markdown, DOCX, and PDF.
- Embeddable data-plane engine — orchestrator-agnostic, no control-plane lock-in ([ADR-0007](docs/adr/0007-two-surface-split-engine-and-control-plane.md)).
- Runs fully air-gapped on the offline leg for privacy-sensitive documents.

## How

```bash
make install                                                           # uv sync
make run_local SAMPLE=samples/legal/us/us-open-government-act-2007.pdf  # offline leg, no API key
```

Full run surface (both legs, CLI switches, `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL`), the devcontainer, and on-demand installs → [CONTRIBUTING.md](CONTRIBUTING.md).

## Why

Incumbent document pipelines tend to couple extraction to one cloud vendor or a heavyweight hosted service. doc-pipeline-engine keeps the engine embeddable and contract-gated instead: the same Pydantic contracts drive the offline and cloud legs interchangeably, so you can start air-gapped and add a cloud leg later without rewiring. See [docs/architecture.md](docs/architecture.md).

## Refs

- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Decisions (ADRs)](docs/adr/index.md)
- Landscape: [ingest](docs/landscape/ingest.md) · [process](docs/landscape/process.md) · [output](docs/landscape/output.md) · [E2E systems](docs/landscape/e2e-systems.md) · [domain extraction](docs/landscape/domain-extraction.md)
- [Scraping landscape](https://github.com/qte77/polyfetch-scrape/blob/main/docs/scraping-landscape.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)

## License

[Apache-2.0](LICENSE) (SPDX: `Apache-2.0`). Bundled third-party sample content is attributed in [NOTICE](NOTICE).
