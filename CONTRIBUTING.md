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
`.devcontainer/devcontainer.json` (Python 3.13 + Claude Code +
ruff/markdownlint/lychee). On rebuild it runs `make setup_uv` then
`make setup_dev`.

### On-demand use-case installs

System-level deps that only some workflows need are installed by their
use case (apt + Python extra + model in one target):

| Command | Use case |
| --- | --- |
| `make install_image_ocr` | Extract image samples (installs `tesseract-ocr` + `tesseract-ocr-eng`) |
| `make install_local_nlp` | Run `local` leg with NER entities (installs `--extra local` + spaCy `en_core_web_sm`) |

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
| `anthropic_sdk` | Anthropic Python SDK for the `anthropic_sdk` leg (vendor-configurable via `base_url` / Bedrock / Vertex) | **Cloud** by default |
| `local` | spaCy + Jinja2 for the `local` leg (no LLM, no cloud calls) | Local |
| `local-render` | Jinja2 only — for environments where spaCy can't install (e.g. Python 3.14) | Local |
| `local-eval` | DeepEval faithfulness probe (wired by harness) | Local |
| `v1` / `v2` / `v2-render` / `v2-eval` | **Deprecated** aliases of the renamed extras above; will be removed in §0.5.0 | (forwards to the new names) |

Install per leg:

```bash
uv sync --extra extract --extra render --extra anthropic_sdk   # anthropic_sdk leg
uv sync --extra extract --extra render --extra local           # local leg, full
make install_local_nlp                                         # spaCy en_core_web_sm
```

### Running the pipeline

`make run_local SAMPLE=path` runs the offline `local` leg with **no API key**
(`make help` lists every recipe). It wraps the harness entry point, which runs
both legs when given a key:

```bash
python -m doc_pipeline_engine.harness <sample> [--local-only] [--output-dir DIR] [--anthropic-sdk-model M]
```

| Env | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | Required only for the `anthropic_sdk` leg; the `local` leg needs none |
| `ANTHROPIC_BASE_URL` | Optional — Anthropic SDK `base_url` for a self-hosted / gateway / Bedrock / Vertex endpoint |

Outputs land in `<output-dir>/<sha>/<leg>/summary.{md,docx,pdf}` (`outputs/` for
`make run_local`; gitignored).

## Quality commands

| Command | Purpose |
| --- | --- |
| `make install_local_nlp` | Install `--extra local` + spaCy `en_core_web_sm` (needed for `local` leg NER) |
| `make install_image_ocr` | Install Tesseract + `eng` (needed for image-sample extraction) |
| `make test` | Full pytest suite |
| `make test_contracts` | JSON schema round-trip tests only |
| `make test_rerun` | Rerun only failed tests (`pytest --lf -x`) — fast TDD iteration |
| `make test_fix_snapshots` | Auto-fix inline-snapshot expected values |
| `make lint` | Ruff check on Python sources |
| `make lint_md` | markdownlint on `**/*.md` (MD013 disabled) |
| `make lint_links` | lychee link check |
| `make validate` | Pre-commit gate: lint + test + lint_md + lint_links |
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
- Add a changelog fragment for non-trivial changes (see below)

## Changelog fragments

`CHANGELOG.md` is assembled by [scriv](https://scriv.readthedocs.io) from per-PR
fragments under `changelog.d/`, so PRs no longer collide on a shared `## [Unreleased]`
block (see [ADR-0012](docs/adr/0012-scriv-managed-changelog.md)).

Every non-trivial PR adds a fragment: run `make changelog_new`, then pick a category
(`Added` / `Changed` / `Fixed` / …) and write a bullet ending with the issue/PR ref
(`(#NNN)`). The other `changelog_*` targets (`make help`) preview and collect fragments;
collection into `CHANGELOG.md` runs at release time.

## Releasing

SemVer; the version lives only in `pyproject.toml` `[project].version` (synced to the
README badge by [bump-my-version](https://github.com/callowayproject/bump-my-version)).
Maintainer flow:

1. Run **bump-my-version** (`patch` / `minor` / `major`) from the Actions tab. It bumps
   `pyproject.toml` + the README badge, syncs `uv.lock`, collects the
   [changelog fragments](#changelog-fragments) into `CHANGELOG.md`, and opens a
   `chore(release): bump …` PR.
2. The PR is bot-authored, so its checks idle at `action_required` — push any commit to
   the bump branch (or close + reopen) to trigger them.
3. Merge on green. **tag-release** then fires on `main` and tags the merge commit
   `vX.Y.Z` — always reachable from `main`, no tag drift.
4. Optionally run **publish-release** for a GitHub Release with notes from the
   `CHANGELOG.md` block. The default flow is tag-only.

## Documentation hierarchy

Authoritative sources — update these, don't duplicate:

- `README.md` — project overview, quickstart
- `docs/architecture.md` — design decisions, contracts, runtime modes
- `docs/roadmap.md` — versioned milestones (0.1 → 0.6+)
- `docs/landscape/ingest.md` — ingest survey (extraction backends, source connectors, crawling)
- `docs/landscape/process.md` — process survey (chunking, NER, RAG indexing, normalization)
- `docs/landscape/output.md` — output survey (rendering, office formats, templating, conformance)
- `docs/landscape/e2e-systems.md` — E2E pipeline systems survey, prior art, and USP positioning
- `docs/landscape/domain-extraction.md` — domain-specific fine-tuned extraction models per industry (biomedical, legal, financial, cybersecurity, ...) for §0.5.0 domain packs
- `docs/prototype/plan.md` — dual-variant E2E prototype plan (Claude Code vs landscape tools)
- `AGENTS.md` — AI agent behavioral rules
- `CONTRIBUTING.md` — this file

## Questions

Open an issue. Agents should escalate via `AGENT_REQUESTS.md`.
