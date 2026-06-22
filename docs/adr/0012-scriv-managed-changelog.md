---
title: ADR-0012 — scriv-managed changelog via per-PR fragments
purpose: Records the move from a hand-edited CHANGELOG.md to scriv-collected per-PR fragments under changelog.d/, adopting the qte77 estate convention
created: 2026-06-22
updated: 2026-06-22
validated_links: 2026-06-22
category: technical
---

## Status

Accepted — 2026-06-22

## Context and Problem Statement

`CHANGELOG.md` is hand-edited: every non-trivial PR appends to the same
`## [Unreleased]` block. Because squash-merges serialise onto one set of lines,
concurrent PRs collide there repeatedly — a recurring, low-value merge-conflict
tax. The qte77 estate (`paperverse`, `analyze-stock-kpi`) already standardised on
[scriv](https://scriv.readthedocs.io): each PR drops a small fragment under
`changelog.d/`, and fragments are collected into `CHANGELOG.md` at release time.

The question: adopt the estate's scriv convention here, or keep hand-editing?

## Decision Drivers

- Eliminate the recurring `## [Unreleased]` merge conflicts (separate files never collide).
- Estate consistency — same changelog workflow across qte77 repos.
- Preserve the existing [Keep a Changelog](https://keepachangelog.com/) format and categories.
- No new non-Python runtime (per [ADR-0008](0008-hatchling-and-uv-over-setuptools-and-pip.md)).

## Considered Options

### Option 1 — scriv-managed `changelog.d/` (estate convention)

- Good, because per-PR fragment files never conflict on merge.
- Good, because it matches the estate; one mental model across repos.
- Good, because scriv is a pure-Python `uv` dev dep; categories mirror the existing preamble.
- Bad, because contributors must learn `make changelog_new` (one command).

### Option 2 — keep the hand-edited `CHANGELOG.md`

- Good, because zero change.
- Bad, because the `## [Unreleased]` conflict tax persists and diverges from the estate.

### Option 3 — auto-generate from Conventional Commits (e.g. git-cliff)

- Good, because no manual fragment step.
- Bad, because it ties changelog quality to commit messages, is not the estate tool, and
  re-derives history rather than curating it.

## Decision Outcome

Chosen: **Option 1**. `[tool.scriv]` config in `pyproject.toml`, fragments under
`changelog.d/`, and `changelog_*` make targets; the contributor workflow lives in
[CONTRIBUTING.md](../../CONTRIBUTING.md#changelog-fragments). `scriv collect` assembles
the next version's entry at the `<!-- scriv-insert-here -->` marker — wired into the
release workflow in [#134](https://github.com/qte77/doc-pipeline-engine/issues/134).
The prior `## [Unreleased]` body was migrated verbatim into a one-time seed fragment so
it lands in the next release.

Deferred: the optional `docs/adr/` → `docs/decisions/` rename (issue #129) — no
functional gain and it breaks inbound links.

## More Information

- scriv: <https://scriv.readthedocs.io>
- Estate reference: `qte77/paperverse`, `qte77/analyze-stock-kpi`
- Related: [ADR-0008](0008-hatchling-and-uv-over-setuptools-and-pip.md) (Python-native / `uv`)
