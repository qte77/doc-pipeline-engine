---
title: ADR-0006 — Apache-2.0 with NOTICE over MIT
purpose: Records the decision to license doc-pipeline-engine under Apache-2.0 and maintain a NOTICE file for third-party sample content
created: 2026-05-25
updated: 2026-05-25
validated_links: 2026-05-25
category: technical
---

## Status

Accepted — 2026-05-25

## Context and Problem Statement

`doc-pipeline-engine` ships a `samples/` directory that bundles third-party
documents under mixed licenses: US Public Domain, UK OGL v3, CC-BY 4.0,
CC-BY-SA, arXiv non-exclusive, IETF Trust, EU Reuse Policy, World Bank Open
Access, and Apache-2.0. These materials require attribution and a clear
separation from the engine's own license. A license that provides a NOTICE
file convention and a patent grant was needed to satisfy both the
redistribution stance and the downstream consumers (polyforge,
office-polyforge) that embed the engine.

## Decision Drivers

- `samples/` contains content under mixed third-party licenses requiring
  per-file attribution in a NOTICE file
- Downstream consumers (polyforge, office-polyforge) are Apache-2.0; clean
  inheritance requires the same license
- Patent grant protects contributors and consumers; MIT and BSD-3-Clause lack
  this

## Considered Options

### Option 1 — Apache-2.0 with NOTICE file

- Good, because includes explicit patent grant protecting contributors and users
- Good, because NOTICE file convention is the canonical place to carry
  per-file third-party attribution
- Good, because Apache-2.0 → Apache-2.0 inheritance is clean for polyforge
  and office-polyforge; MIT consumers also accept Apache-2.0
- Bad, because slightly more ceremony than MIT for pure OSS projects without
  mixed third-party content

### Option 2 — MIT

- Good, because minimal license text; widest compatibility
- Bad, because no patent grant
- Bad, because no NOTICE convention; third-party attribution must be handled
  ad hoc

### Option 3 — BSD-3-Clause

- Good, because simple permissive license
- Bad, because no patent grant
- Bad, because no NOTICE convention; same attribution problem as MIT

### Option 4 — MPL-2.0

- Good, because file-level copyleft is a reasonable middle ground
- Bad, because file-level copyleft adds friction for embedders who modify
  engine source files

## Decision Outcome

Chosen: **Option 1**. `pyproject.toml` declares `license = "Apache-2.0"` and
`license-files = ["LICENSE", "NOTICE"]`. The `NOTICE` file carries the
complete per-license catalogue for `samples/` content and defers to
`samples/SAMPLES.md` for per-file attribution. Downstream Apache-2.0
consumers inherit cleanly; MIT consumers are also compatible.

## More Information

- Apache License 2.0: <https://www.apache.org/licenses/LICENSE-2.0>
- ADR-0010 (samples gitignored): [0010-samples-gitignored-with-download-script-as-sot.md](0010-samples-gitignored-with-download-script-as-sot.md)
- ADR-0005 (Kreuzberg ELv2 boundary): [0005-kreuzberg-elv2-license-boundary.md](0005-kreuzberg-elv2-license-boundary.md)
