# doc-pipeline-engine

[![License](https://img.shields.io/badge/license-Apache_2.0-58f4c2.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-0.1.0-58f4c2.svg)
[![CodeQL](https://github.com/qte77/doc-pipeline-engine/actions/workflows/codeql.yaml/badge.svg)](https://github.com/qte77/doc-pipeline-engine/actions/workflows/codeql.yaml)

Modular document processing engine with contract-gated pipeline stages. Standalone module — usable independently or as a component in larger systems (e.g. polyforge, office-polyforge).

## Quickstart

```bash
make install        # uv sync
make test-contracts # schema round-trip tests
```

## Docs

- [Architecture](docs/architecture.md) — stage graph, runner vs stream, package layout
- [Roadmap](docs/roadmap.md) — milestones with reasoning and implementation notes
- [Scraping Landscape](docs/scraping-landscape.md) — web scraping and extraction tool survey
- [Changelog](CHANGELOG.md) — release history ([semver](https://semver.org/))
- [v0.1 design](docs/plans/v0.1-init.md) — original planning doc
