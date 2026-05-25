---
title: ADR-0008 — Hatchling + uv over setuptools + pip
purpose: Records the decision to use Hatchling as the build backend and uv as the package manager and task runner
created: 2026-05-25
updated: 2026-05-25
validated_links: 2026-05-25
category: technical
---

## Status

Accepted — 2026-05-25

## Context and Problem Statement

A build backend and package manager must be chosen for the project. The
requirements are PEP 621 native configuration in `pyproject.toml`, fast
dependency resolution for CI, and a clean dev workflow without legacy
`setup.py` or separate `requirements.txt` files. `uv sync` replaces pip
everywhere in the Makefile — install, test, lint, docs, and script execution
all go through `uv run`.

## Decision Drivers

- PEP 621 compliance: all metadata in `pyproject.toml`, no secondary config
  files
- Fast resolution and install speed for CI and devcontainer startup
- No `setup.py` or `setup.cfg` legacy baggage
- Single tool (`uv`) covers sync, run, and extras across all Makefile targets

## Considered Options

### Option 1 — Hatchling + uv

- Good, because Hatchling is lightweight, PEP 517/660 native, zero config
  for standard layouts
- Good, because `uv sync` is significantly faster than pip for resolution and
  install
- Good, because `uv run` replaces `python -m` / `pip run` uniformly; single
  tool across all Makefile targets
- Bad, because uv is a newer tool; not all environments have it pre-installed
  (mitigated by the `setup_uv` Makefile target)

### Option 2 — setuptools + pip

- Good, because ubiquitous; every Python environment has pip
- Bad, because requires `setup.py` or `setup.cfg` alongside `pyproject.toml`
  for full feature coverage
- Bad, because significantly slower resolution than uv
- Bad, because legacy `setup.py` baggage is a maintenance burden

### Option 3 — PDM + pip

- Good, because PEP 621 native and well-regarded
- Bad, because narrower adoption than uv; fewer devcontainer base images
  include it

### Option 4 — Poetry

- Good, because mature ecosystem with lockfile support
- Bad, because `pyproject.toml` dialect drift: Poetry uses non-standard keys
  that can conflict with PEP 621
- Bad, because Poetry's lockfile format is not interoperable with uv or pip

## Decision Outcome

Chosen: **Option 1**. `pyproject.toml` declares `requires = ["hatchling"]`
and `build-backend = "hatchling.build"`. Every Makefile target that runs
Python or installs deps uses `uv run` or `uv sync`. The `setup_uv` target
bootstraps uv via pip for environments that don't have it, keeping the
dependency on pip minimal and one-time.

## More Information

- Hatchling: <https://hatch.pypa.io/latest/config/build/>
- uv: <https://docs.astral.sh/uv/>
- PEP 621: <https://peps.python.org/pep-0621/>
