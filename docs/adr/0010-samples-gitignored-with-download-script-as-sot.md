---
title: ADR-0010 — Samples gitignored with download script as single source of truth
purpose: Records the decision to exclude binary sample files from git and use a download script as the authoritative manifest
created: 2026-05-25
updated: 2026-05-25
validated_links: 2026-05-25
category: technical
---

## Status

Accepted — 2026-05-25

## Context and Problem Statement

The `samples/` directory holds approximately 95 binary files (PDFs, images,
Office documents, and other formats) used for pipeline testing and
demonstration. These files are too large for git's object store and carry
mixed third-party licenses. A strategy is needed for how contributors
reproduce the sample corpus without committing binaries to the repository.

## Decision Drivers

- ~95 binary files at MB scale are too large for git without degrading
  `git clone` performance
- Each file has a distinct license and must carry attribution metadata
  (URL, license, description)
- Reproduction must be deterministic: same script, same corpus
- License metadata must live in code, not in a separate wiki or doc

## Considered Options

### Option 1 — Download script + `samples/` gitignored

- Good, because repo stays small; `git clone` is fast
- Good, because the script (`scripts/download-samples.sh`) carries URL,
  license, and description metadata per file — license metadata as code
- Good, because `--manifest` mode regenerates `samples/SAMPLES.md` without
  re-downloading, making attribution refresh cheap
- Bad, because corpus reproduction requires an internet connection and a
  manual `scripts/download-samples.sh --download` run

### Option 2 — Git LFS

- Good, because binaries stay in git history; no separate download step
- Bad, because ~95 MB-scale files exhaust LFS quota on GitHub's free tier
- Bad, because LFS adds CI complexity (credential setup, pointer management)
- Bad, because LFS is GitHub-specific; lock-in risk if the repo moves

### Option 3 — Commit binaries directly

- Good, because zero setup; `git clone` gives everything
- Bad, because repo bloat degrades `git clone` performance for all
  contributors
- Bad, because no structured license-metadata layer; attribution is static
  text only

### Option 4 — External CDN with hash manifest

- Good, because binaries are served fast from a CDN
- Bad, because requires additional infrastructure to host and maintain
- Bad, because no clear win over the download script; adds an out-of-repo
  dependency

## Decision Outcome

Chosen: **Option 1**. `samples/` is listed in `.gitignore`. The download
script `scripts/download-samples.sh` is the single source of truth: it
carries per-file metadata and regenerates `samples/SAMPLES.md` on each run.
`NOTICE` references `samples/SAMPLES.md` as the per-file attribution index.

## More Information

- ADR-0006 (Apache-2.0 + NOTICE): [0006-apache-2-0-with-notice-over-mit.md](0006-apache-2-0-with-notice-over-mit.md)
- Download script: [../../scripts/download-samples.sh](../../scripts/download-samples.sh)
