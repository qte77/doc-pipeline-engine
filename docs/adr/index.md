---
title: Architectural Decision Records
purpose: Index of all ADRs for doc-pipeline-engine; one line per record with status and scope
created: 2026-05-25
updated: 2026-05-26
validated_links: 2026-05-26
category: technical
---

This project records architectural decisions as
[MADR 3.x](https://adr.github.io/madr/) Markdown files. Each ADR is
immutable once accepted; superseded decisions are kept and cross-linked
from the replacement.

## Status legend

- **Accepted** — in effect; do not edit retroactively
- **Proposed** — under discussion; may change before acceptance
- **Superseded by ADR-NNNN** — historical; see the linked replacement
- **Deprecated** — no longer in effect; not yet superseded

## Records

| # | Title | Status | Scope |
| --- | --- | --- | --- |
| [0001](0001-pydantic-as-contract-source-of-truth.md) | Pydantic as the contract source of truth | Accepted (2026-04-27) | Contracts: Pydantic v2 models replace JSON Schema files |
| [0002](0002-mkdocs-material-mkdocstrings-for-api-docs.md) | mkdocs-material + mkdocstrings for API docs | Accepted (2026-04-27) | Docs site: theme, plugin chain, GH Pages deploy |
| [0003](0003-rename-legs-anthropic-sdk-local.md) | Rename pipeline legs `v1` → `anthropic_sdk`, `v2` → `local` | Accepted (2026-04-27) | Pipeline: self-describing leg names ahead of external evaluators |
| [0004](0004-external-evaluators-vs-pipeline.md) | External evaluators vs the in-process pipeline | Accepted (2026-04-27) | Prototype: one-shot summarizers live in `external/`, not as stages |
| [0005](0005-kreuzberg-elv2-license-boundary.md) | Pin Kreuzberg below v4.8 to stay on the MIT line; gate ELv2 as opt-in | Accepted (2026-05-26) | Licence: cap `kreuzberg<4.8`; ship v4.8+ behind `[kreuzberg-elv2]` extra |
| [0006](0006-apache-2-0-with-notice-over-mit.md) | Apache-2.0 with NOTICE over MIT | Accepted (2026-05-25) | Licence: patent grant + NOTICE for mixed-licence samples content |
| [0007](0007-two-surface-split-engine-and-control-plane.md) | Two-surface split: engine (data plane) vs control plane | Accepted (2026-05-25) | Architecture: engine stays embeddable; orchestrator-agnostic via contracts |
| [0008](0008-hatchling-and-uv-over-setuptools-and-pip.md) | Hatchling + uv over setuptools + pip | Accepted (2026-05-25) | Toolchain: PEP 621 native; `uv sync` replaces pip everywhere |
| [0009](0009-ten-contracts-with-five-simplified-stubs.md) | 10 contracts shipped with 5 simplified stubs | Accepted (2026-05-25) | Contracts: slot reservation; ClassificationManifest / FormatMatch / FormatConformance / InputFormat / OutputFormat as stubs |
| [0010](0010-samples-gitignored-with-download-script-as-sot.md) | Samples gitignored via download script as single source of truth | Accepted (2026-05-25) | Samples: `scripts/download-samples.sh` is SoT; binaries not in git |

## Adding a new ADR

1. Copy the structure from any recent ADR (e.g.,
   [0005](0005-kreuzberg-elv2-license-boundary.md)) — it follows MADR 3.x.
2. Filename: `NNNN-title-in-kebab-case.md` where `NNNN` is the next
   four-digit number.
3. Add a row to the **Records** table above.
4. ADRs use `## More Information` (not `## Sources`) per the
   [frontmatter convention ADR exception](../../.claude/rules/frontmatter-convention.md#adr-exception-madr-3x).

## More Information

- MADR 3.x spec: <https://adr.github.io/madr/>
- ADR pattern background: <https://adr.github.io/>
