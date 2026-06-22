<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Added

- `docs/prototype/results/2026-06-22-local-leg-examples.md` — reference `local`-leg summaries (claims + spaCy NER entities) for three redistribution-clean samples (UK-OGL contract, US-PD OPEN Government Act, US-PD NIST SP 800-63B), reproducible via `make run_local`.
- `harness.run_local()` + `python -m doc_pipeline_engine.harness <sample> --local-only` + `make run_local SAMPLE=…` — run the offline `local` leg with **no `ANTHROPIC_API_KEY`**. The documented run path was all-or-nothing (`run_both` fired the paid `anthropic_sdk` leg first and died without a key). README + CONTRIBUTING now document the run surface: commands, the `--local-only` / `--output-dir` / `--anthropic-sdk-model` switches, and `ANTHROPIC_API_KEY` (anthropic leg only) / `ANTHROPIC_BASE_URL` (self-hosted / gateway / Bedrock / Vertex). (#133)
- `.github/workflows/tests.yaml` — CI gate running the documented `uv sync --extra …` install + `ruff` + `pytest` on Python 3.13 (SHA-pinned actions). Closes the gap that let the broken install (#132) and the render regression (#131) ship — no Python test/lint workflow existed before. (#132)
- `.python-version` (`3.13`) — pin uv / Codespaces / CI to the supported full-stack Python; `requires-python>=3.11` keeps the 3.14 render-only path. (#132)

### Changed

- `tests/test_fixtures.py::test_domains_discovered` — skip when `samples/` is absent (gitignored corpus), so the suite runs in CI / fresh clones without the download. (#132)
- `.github/dependabot.yaml` — `ignore` `kreuzberg>=4.8` so dependabot stops proposing to cross the ELv2 licence boundary ([ADR-0005](docs/adr/0005-kreuzberg-elv2-license-boundary.md)); closed stale PR #111 (which widened `<4.8` → `<4.10`). (#115)
- `.markdownlint-cli2.jsonc` — allow `<details>`/`<summary>` (MD033 `allowed_elements`) so `make lint_md` passes on the `docs/architecture.md` collapsible. (#113)
- `docs/assets/architecture-bird.svg` → `docs/assets/images/architecture-bird.svg`: relocated under an `images/` subdirectory to match the cross-repo convention now shared with `qte77/utils-pseudonomyze-text`. Reference in `docs/architecture.md` updated.
- `docs/architecture.md`: bird's-eye SVG embed wrapped in a collapsed `<details>` block (summary "Architecture overview (click to expand)") so the doc stays scannable.
- `docs/assets/images/architecture-bird.svg` `<style>`: added `@media (max-width: 600px)` rule that hides the three lane labels (`.lane-label`, `.lane-sub`) below 600 px rendered width, where they become illegible.

### Removed

- Bird's-eye SVG embed at the top of `README.md`. The diagram now lives only in `docs/architecture.md` (collapsed) — README top is reserved for orientation (name, badges, value prop).

### Fixed

- `pyproject.toml` — add `[tool.uv] conflicts` for the mutually-exclusive `extract` (kreuzberg<4.8) / `kreuzberg-elv2` (kreuzberg>=4.8) extras (the ADR-0005 licence boundary). Without it, `uv lock` / `uv sync` / `make install` / `uv sync --extra …` failed "unsatisfiable" on Python 3.13 **and** 3.14 — the documented install was broken; only `--frozen` worked. `uv.lock` regenerated. (#132)
- `stages/local_render.py` + `stages/anthropic_sdk_render.py`: accept the typed `AnalysisReport` (attribute access; `model_dump(mode="json")` for the anthropic prompt) instead of dict-subscripting it. The #127 typed-return refactor left these two render stages un-migrated, so the harness legs crashed with `TypeError: 'AnalysisReport' object is not subscriptable`; the render unit tests masked it by passing dicts (now build real models). (#130)
- `docs/landscape/ingest.md` marker row — corrected the stale "depends on surya (GPL-3.0)" claim: surya's LICENSE is Apache-2.0 (weights are RAIL-M, free < $5M rev) and marker's GPL-3.0 is its own code. Verified by direct LICENSE-file inspection. (#112)
- `docs/roadmap.md` § 0.2.2: status `in progress` → `done` — all Delivered items shipped, ADR-0002 Accepted.
- `docs/roadmap.md` § 0.2.2: stale claim "embedded in `docs/architecture.md` and `README.md`" replaced — SVG now only in `docs/architecture.md` (inside `<details>`) at the new `docs/assets/images/` path.
- `docs/roadmap.md` § 0.2.3: status updated — PR A (#54) and PR B delivered; only PR C (CC SDK) remains deferred (gated on `claude-agent-sdk` PyPI availability).
- `docs/roadmap.md` § Future PDF roundtrip bullet: broken cross-repo anchor `pseudonymize-text/.../USAGE.md#pdfs-via-doc-pipeline-engine` removed (anchor never existed on the target side); now links to `pseudonymize-text/.../docs/roadmap.md`.
- `docs/roadmap.md` frontmatter: `validated_links` date refreshed to 2026-05-31.
- `docs/adr/index.md`: ADR-0005 row status `Proposed (2026-05-25)` → `Accepted (2026-05-26)` (matched the ADR file's own status header).
- `docs/adr/0002-mkdocs-material-mkdocstrings-for-api-docs.md` § Decision Outcome: nav-claim "ADRs (0001, 0002)" → "ADRs (via `adr/index.md`)" — nav was simplified to a single entry covering all ADRs.
- `docs/adr/0002-…` § Option 4: stale `v2_normalize` module reference updated to `local_normalize` per ADR-0003.
- `docs/adr/0004-external-evaluators-vs-pipeline.md` § Consequences: `V1` / `V2` leg names replaced with `anthropic_sdk` / `local` per ADR-0003 (Consequences should reflect post-decision state).
- `README.md` Devcontainer section: `make install_v2_nlp` → `make install_local_nlp`; surrounding "V1 stages" / "V2 NER entities" wording updated to canonical leg names per ADR-0003.
- `mkdocs.yaml`: `Code: docstrings.md` nav line annotated as build-artifact-generated-at-deploy (per ADR-0002), so a reader doesn't mistake the absent working-tree file for a defect.

### Security

- Pin `extract` extra to `kreuzberg>=2.0,<4.8` to stay on the MIT line
  (v4.7.4 is the last MIT release; upstream relicensed to Elastic License 2.0
  starting at v4.8.0 on 2026-04-08). New opt-in `[kreuzberg-elv2]` extra
  (`kreuzberg>=4.8`) for downstream consumers comfortable with ELv2
  restrictions (no managed-service offering, attribution required). Default
  install path stays Apache-2.0-clean. See
  [ADR-0005](docs/adr/0005-kreuzberg-elv2-license-boundary.md). Resolves #76.

### Added

- `docs/adr/0011-content-layout-owned-by-docling.md` — ADR (MADR 3.x): docling owns `ExtractionBundle.content.layout` (geometry + semantic `kind` + provenance, the shape `CanonicalDoc.source_refs` indexes into); pdfplumber is a born-digital cross-check; **LiteParse** (Node ≥18 subprocess) and **OmniParse** (GPL-3.0 + cc-by-nc-sa NonCommercial weights + GPU) rejected. (#112)
- `docs/landscape/ingest.md` §1 extraction backends — added **olmOCR** (Apache-2.0 VLM OCR scan stub), **pdfplumber** + **pdfminer.six** (MIT, pure-Python bbox/tables), **LiteParse** (Apache-2.0, not adopted — Node-subprocess tax), **OmniParse** (Tier E+F, avoid), plus a `content.layout` ownership note. LiteParse spiked on a 15-page PDF (976 bbox items, ~10.5 s). (#112)
- `docs/architecture.md` "Supported input formats" section (Kreuzberg format coverage; **SVG** not supported → pre-rasterize) + extract-stage docstring pointer. Salvaged from the superseded `feat/external-anthropic-and-cc-cli` branch. (#114)
- Six new ADRs adopting [MADR 3.x](https://adr.github.io/madr/): `0005` Kreuzberg ELv2 licence boundary; `0006` Apache-2.0 + NOTICE over MIT; `0007` two-surface split (engine vs control plane); `0008` Hatchling + uv over setuptools + pip; `0009` 10 contracts with 5 simplified stubs; `0010` samples gitignored via download script as SoT. ADRs 0006–0010 promote decisions previously buried in `docs/architecture.md` lines 78–89. (#97 / #99 / #104)
- `docs/adr/index.md` — MADR-style index page with status legend, Records table, and "Adding a new ADR" guide. Auto-listing target for `mkdocs.yaml` nav. (#97)
- `.claude/rules/frontmatter-convention.md` `## ADR Exception (MADR 3.x)` section — ADRs use `## More Information` instead of `## Sources`; bare-URL precedent preserved. Upstreamed as proposal in qte77/claude-code-plugins#160. (#97)
- New landscape candidates: **Knowhere** (Ontos-AI, Apache-2.0, closest competitor parallel to R2R) and **DocETL** (UC Berkeley EPIC) in `e2e-systems.md`; **adaptive-chunking** (ekimetrics, MIT, LREC 2026) and **chonkie** / **LightRAG** / **nano-graphrag** / **docling-core** in `process.md`; **MinerU** (Tier-G licence — Apache-2.0 + commercial threshold + attribution + termination), **crawl4ai**, **ColPali**, and **marker** (GPL-3.0 gate) in `ingest.md`. (#95)
- `pyproject.toml` `[kreuzberg-elv2]` opt-in extra at `kreuzberg>=4.8` for consumers explicitly accepting ELv2 restrictions. (#104)

- `docs/landscape/domain-extraction.md` — new sibling landscape file surveying fine-tuned + domain-pretrained extraction models per industry (biomedical, legal, financial, scientific/patents, cybersecurity, HR, retail, agriculture/food, plus sparse-domain sections for mech-elec-cert and government/regulatory). Includes License tier reference (Apache/MIT / BSD / LGPL / CC-BY-SA / CC-BY-NC / GPL-AGPL / Undeclared) and PHI/de-identification cross-cutting note. Distinct from `process.md` (stage-scoped) — this file is domain-scoped.
- `docs/landscape/process.md` §6 — schema-templated extraction landscape (NuExtract3 + outlines/instructor cross-refs). (#81)
- `external/` directory tree — off-the-shelf one-shot summarizers (Anthropic SDK + CC CLI + interactive doc) as comparison baseline. See [ADR-0004](docs/adr/0004-external-evaluators-vs-pipeline.md). (#61)
- `scripts/gen_contracts_md.py` + committed `docs/contracts.md` — auto-generated contracts reference consumed by external evaluators.
- `docs/adr/0004-external-evaluators-vs-pipeline.md` — records external-evaluators decision.
- `docs/roadmap.md` §0.2.3 — describes PR A (merged) + PR B + PR C (deferred CC SDK).
- New tests: `test_external_anthropic_sdk_run_oneshot`, `test_external_cc_cli_run_headless`, `test_gen_contracts_md` (3 each, RED-first).
- `python -m doc_pipeline_engine.models dump <Name>` CLI — emits `Model.model_json_schema()`.
- `tests/test_models_round_trip.py` — round-trip + negative-validation cases over all 10 models.
- `docs/adr/0001-pydantic-as-contract-source-of-truth.md` + `docs/roadmap.md` §0.2.1 entry.
- `mkdocs.yaml` + `.github/workflows/generate-deploy-mkdocs-ghpages.yaml` + `[dependency-groups] docs` extras + `make docs*` targets + [ADR-0002](docs/adr/0002-mkdocs-material-mkdocstrings-for-api-docs.md) + roadmap §0.2.2.
- `tests/test_stages_v2_normalize_headings.py` — five cases for v2 heading reconstruction.
- `docs/prototype/results/2026-04-26-run-3-v2-headings.md` — V2-only re-run after [#33](https://github.com/qte77/doc-pipeline-engine/issues/33).
- `stages/_v1_client.py` backend dispatch (explicit client → SDK → CLI → error) + `tests/test_v1_client_backend_dispatch.py`. Resolves [#30](https://github.com/qte77/doc-pipeline-engine/issues/30).
- `docs/prototype/results/2026-04-26-run-2-v1-cli.md` + `docs/prototype/results/README.md`.
- `.devcontainer/devcontainer.json` + Makefile bootstrap targets (`setup_uv`, `setup_dev`, `setup_claude_code`, `setup_npm_tools`, `setup_lychee`, `install_image_ocr`, `install_v2_nlp`). Resolves [#32](https://github.com/qte77/doc-pipeline-engine/issues/32).
- `.claude/rules/frontmatter-convention.md` + `.markdownlint.json` + plugin config. YAML frontmatter on `docs/landscape/*.md` and `docs/prototype/*.md`.
- `docs/prototype/results/2026-04-26-run-1-v2-only.md`.
- `.github/workflows/generate-sbom.yaml` + `write-llms-txt.yaml` + `.github/templates/llms.txt.tpl`.
- §0.2.0 Runner: `runner.py`, `base/adapter.py`, `stages/__init__.py`, `stages/discover.py`, `stages/extract.py`.
- `pyproject.toml` optional extras: `extract` (kreuzberg), `render` (markdown + python-docx + weasyprint), `anthropic_sdk` (anthropic), `local` / `local-render` / `local-eval`.
- `render/formats.py` — shared Markdown → DOCX + PDF utility.
- `anthropic_sdk` post-extraction stages: `normalize`, `analyze`, `render`, `eval` + `_anthropic_sdk_client.py`.
- `local` post-extraction stages: `normalize`, `analyze`, `render`, `eval` + Jinja template.
- Parallel diff harness `harness.py` — `run_both()` returns `DiffReport`.
- `docs/prototype/samples.md` + `docs/prototype/plan.md` (dual-variant E2E prototype plan).
- `Makefile` `test_rerun` / `test_fix_snapshots` / `validate` targets.
- `docs/landscape/process.md` + `output.md` + `e2e-systems.md` (originally `prior-art.md`, renamed in this cycle).

### Changed

- All existing ADRs (`0001` Pydantic source-of-truth / `0002` mkdocs-material / `0003` leg rename / `0004` external evaluators) retrofitted to MADR 3.x structure: `## Status` heading (was inline bold prose); `## Context and Problem Statement`; new `## Decision Drivers`; `## Considered Options` with `### Option N — name` subsections using MADR-canonical inline `- Good, because …` / `- Bad, because …` bullets; `## Decision Outcome`; `## More Information` (was `## Sources`, bare-URL format preserved). Existing `## Consequences` sections kept verbatim. (#97)
- `mkdocs.yaml` ADR nav simplified from four explicit entries to single `adr/index.md` reference; future ADRs auto-list via the index page without `mkdocs.yaml` edits. (#97)
- `docs/architecture.md` "Design decisions" section: replaced inline 5-decision narrative with one-line cross-refs to ADR-0006…0010; pre-decision "Four orchestration patterns P1–P4" bullet kept inline (no ADR until evaluation lands). (#99)
- `docs/landscape/ingest.md` Kreuzberg row: licence column now `MIT (≤4.7); ELv2 (≥4.8, Tier G)`; cross-link to ADR-0005. (#95 / #97)
- `docs/landscape/process.md`: Flair demoted to **Avoid** (superseded by GLiNER family); GLiNER row expanded with GLiREL (zero-shot relation extraction) + gliner-multitask sibling; Camelot pinned to active fork `camelot-dev/camelot` (atlanhq fork flagged dead); table-transformer upstream flagged dormant; NuExtract3 benchmark caveat strengthened; instructor "cloud-by-default" framing softened (v1.x added ollama + litellm backends); Chroma v0.5+ native BM25 hybrid noted. (#95)
- `docs/landscape/e2e-systems.md` licence corrections: R2R Apache-2.0 → MIT (+ maintenance stall flagged: last commit 2025-11-07); AWS GenAI IDP Apache-2.0 → MIT-0; `sample-aws-idp-pipeline` corrected to Amazon Software License (proprietary, not Apache-2.0; verified by reading LICENSE directly); LlamaIndex rebrand qualifier added; `thetanishqrathore/IDP` expanded scope; `awesome-document-understanding` flagged dormant. Gap-analysis claims 1/5/6 updated (claim 1 strengthened by R2R stall; claim 5 marked aspirational until §0.5.0; claim 6 under pressure). (#95)
- `docs/landscape/output.md` full GitHub-API-verified currency audit (original sweep was network-blocked); `odfpy` licence corrected from claimed Apache-2.0/LGPL-2.1 to actual Apache-2.0 + GPL-2.0 dual (treat as GPL-2.0 for distribution); Quarto/Sphinx licences confirmed by direct LICENSE-file reads. (#95)
- `docs/llms.txt` + `.github/templates/llms.txt.tpl` — landscape entry repointed at `e2e-systems.md` (was stale `prior-art.md` 404 from earlier rename in #83); link label "Prior art" → "E2E systems". CI lychee did not catch this (scans `**/*.md` only; `llms.txt` is `.txt`). (#101)
- Rename `docs/landscape/prior-art.md` → `e2e-systems.md` (+ companion-link updates in three sibling landscape files + `mkdocs.yaml` nav + `README.md` + `CONTRIBUTING.md` + `docs/prototype/plan.md`) + GLM-OCR References URL fix in `ingest.md` (`zai-org/GLM-4` → `zai-org/GLM-OCR`). (#83)
- Enable Ruff `S` (bandit) and `C90` (mccabe, `max-complexity=10`); `tests/**` get `S101` ignore. Resolves #72; follow-up #75 tracks remaining rules. (#79)
- Migrate markdown linting from `markdownlint-cli` to `markdownlint-cli2` (single-file config in `.markdownlint-cli2.jsonc`).
- Bird's-eye architecture SVG redrawn with three lanes (anthropic_sdk + local + external evaluators side-panel); later relocated to `docs/assets/images/architecture-bird.svg` per the Changed entry above.
- Pipeline legs renamed: `v1` → `anthropic_sdk`, `v2` → `local`. Output dirs, extras, Makefile targets, CLI flag, and stage filenames updated. Deprecated aliases ship for one cycle. See [ADR-0003](docs/adr/0003-rename-legs-anthropic-sdk-local.md).
- Pydantic v2 models replace the JSON-Schema gate as the contract source-of-truth. See [ADR-0001](docs/adr/0001-pydantic-as-contract-source-of-truth.md).
- `stages/local_normalize.py` (formerly `v2_normalize`) — flat heading tree via three regex families with 50% density-cap fallback. Resolves [#33](https://github.com/qte77/doc-pipeline-engine/issues/33).
- Reorganize docs into topical subdirs: `landscape-*.md` → `landscape/*.md`, `prototype-*.md` → `prototype/*.md`.
- `.claude/settings.json` enables `python-dev` and `commit-helper` plugins; `CONTRIBUTING.md` documents the plugin set.

### Removed

- `docs/landscape/e2e-systems.md` entry for `aws-samples/document-processing-pipeline-for-regulated-industries` — dormant since 2021-10-25 (4+ years stale); no longer a useful reference. (#95)
- CC-CLI fallback in `stages/_anthropic_sdk_client.py` (rolled back from #41/#30). Subscription-only users now run `external/cc_cli/run_headless.sh`. Three CLI-dispatch tests removed; explicit-client + SDK + no-API-key tests preserved.
- `contracts/` directory (10 hand-written JSON Schema files) — superseded by Pydantic models per [ADR-0001](docs/adr/0001-pydantic-as-contract-source-of-truth.md). `tests/test_contracts.py` and the `jsonschema` runtime dep gone with it.

### Fixed

- `anthropic_sdk` leg of the parallel-diff harness runs in subscription-only environments (claude CLI but no `ANTHROPIC_API_KEY`). Previously crashed at `_anthropic_sdk_client.make_client()`.
- `_anthropic_sdk_client._call_via_cli` passes the user prompt via stdin (was hitting argv length limit on the 220K-char contract DOCX).

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
