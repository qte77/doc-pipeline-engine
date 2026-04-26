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

A reproducible Codespaces / VS Code dev container lives at
`.devcontainer/setup_dev/devcontainer.json` (Python 3.13 + Claude Code +
ruff/markdownlint/lychee). On rebuild it runs `make setup-uv` then
`make setup-dev`.

### On-demand use-case installs

System-level deps that only some workflows need are installed by their
use case (apt + Python extra + model in one target):

| Command | Use case |
| --- | --- |
| `make install-image-ocr` | Extract image samples (installs `tesseract-ocr` + `tesseract-ocr-eng`) |
| `make install-v2-nlp` | Run V2 leg with NER entities (installs `--extra v2` + spaCy `en_core_web_sm`) |

Claude Code plugins declared in `.claude/settings.json`
(`python-dev`, `commit-helper` from `qte77-claude-code-utils`,
`context7` from `claude-plugins-official`) provide the testing and
commit-workflow conventions used in this repo. `rag-core` will be
enabled when §0.5 indexing wiring begins.

### Optional extras

The prototype's pipeline legs are gated behind `[project.optional-dependencies]`:

| Extra | Purpose | Locality |
| --- | --- | --- |
| `extract` | Kreuzberg extractor (PDF/Office/images/email/text) | Local |
| `render` | Markdown → DOCX + PDF (markdown / python-docx / WeasyPrint) | Local |
| `v1` | Anthropic SDK for V1 (Claude API) leg | **Cloud** |
| `v2` | spaCy + Jinja2 for V2 (Python tools) leg | Local |
| `v2-render` | Jinja2 only — for environments where spaCy can't install (e.g. Python 3.14) | Local |
| `v2-eval` | DeepEval faithfulness probe (wired by harness) | Local |

Install per leg:

```bash
uv sync --extra extract --extra render --extra v1   # V1 leg
uv sync --extra extract --extra render --extra v2   # V2 leg, full
make install-v2-nlp                                  # spaCy en_core_web_sm
```

## Quality commands

| Command | Purpose |
| --- | --- |
| `make install-v2-nlp` | Install `--extra v2` + spaCy `en_core_web_sm` (needed for V2 NER) |
| `make install-image-ocr` | Install Tesseract + `eng` (needed for image-sample extraction) |
| `make test` | Full pytest suite |
| `make test-contracts` | JSON schema round-trip tests only |
| `make test-rerun` | Rerun only failed tests (`pytest --lf -x`) — fast TDD iteration |
| `make test-fix-snapshots` | Auto-fix inline-snapshot expected values |
| `make lint` | Ruff check on Python sources |
| `make lint-md` | markdownlint on `**/*.md` (MD013 disabled) |
| `make lint-links` | lychee link check |
| `make validate` | Pre-commit gate: lint + test + lint-md + lint-links |
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
- `docs/landscape/ingest.md` — ingest survey (extraction backends, source connectors, crawling)
- `docs/landscape/process.md` — process survey (chunking, NER, RAG indexing, normalization)
- `docs/landscape/output.md` — output survey (rendering, office formats, templating, conformance)
- `docs/landscape/prior-art.md` — E2E pipeline prior art and USP positioning
- `docs/prototype/plan.md` — dual-variant E2E prototype plan (Claude Code vs landscape tools)
- `AGENTS.md` — AI agent behavioral rules
- `CONTRIBUTING.md` — this file

## Questions

Open an issue. Agents should escalate via `AGENT_REQUESTS.md`.
