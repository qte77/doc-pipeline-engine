# Contributing

Technical workflows, commands, and conventions for human contributors and AI
agents. For agent behavioral rules see [AGENTS.md](AGENTS.md). For project
overview see [README.md](README.md).

## Setup

```bash
make install        # uv sync — install dev dependencies
```

Requires [uv](https://github.com/astral-sh/uv). Python version pinned in
`pyproject.toml`.

Claude Code plugins declared in `.claude/settings.json`
(`python-dev`, `commit-helper` from `qte77-claude-code-utils`,
`context7` from `claude-plugins-official`) provide the testing and
commit-workflow conventions used in this repo. `rag-core` will be
enabled when §0.5 indexing wiring begins.

## Quality commands

| Command | Purpose |
| --- | --- |
| `make test` | Full pytest suite |
| `make test-contracts` | JSON schema round-trip tests only |
| `make lint` | Ruff check on Python sources |
| `make lint-md` | markdownlint on `**/*.md` (MD013 disabled) |
| `make lint-links` | lychee link check |
| `make clean` | Remove `.pytest_cache`, `.ruff_cache`, `__pycache__` |
| `make help` | List all recipes |

Add `VERBOSE=1` to any target for full output.

## Code style

- **Imports**: absolute (`from doc_pipeline_engine.module import X`)
- **Comments**: default to none; add `# Reason:` only when the *why* is
  non-obvious
- **Dependencies**: verify in `pyproject.toml` before importing — never
  hallucinate libraries
- **Tests**: mirror `src/` layout under `tests/`; new functionality requires
  tests

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` user-facing capability
- `fix:` bug fix
- `docs:` documentation only
- `chore:` tooling, deps, non-user-facing
- `refactor:` no behavior change
- `test:` tests only

Sign commits (GPG required by branch ruleset). See `.gitmessage` for the
project commit template.

## Pull requests

- One concern per PR — keep diffs focused
- Reference related issues (`Closes #N`)
- All required CI checks must be green before merge (CodeQL, CodeFactor)
- Squash-merge only (enforced by ruleset)
- Update `CHANGELOG.md` for non-trivial changes

## Documentation hierarchy

Authoritative sources — update these, don't duplicate:

- `README.md` — project overview, quickstart
- `docs/architecture.md` — design decisions, contracts, runtime modes
- `docs/roadmap.md` — versioned milestones (0.1 → 0.6+)
- `docs/landscape-ingest.md` — ingest survey (extraction backends, source connectors, crawling)
- `docs/landscape-process.md` — process survey (chunking, NER, RAG indexing, normalization)
- `docs/landscape-output.md` — output survey (rendering, office formats, templating, conformance)
- `docs/landscape-prior-art.md` — E2E pipeline prior art and USP positioning
- `docs/prototype-plan.md` — dual-variant E2E prototype plan (Claude Code vs landscape tools)
- `AGENTS.md` — AI agent behavioral rules
- `CONTRIBUTING.md` — this file

## Questions

Open an issue. Agents should escalate via `AGENT_REQUESTS.md`.
