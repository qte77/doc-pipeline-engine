---
title: ADR-0005 — Pin Kreuzberg below v4.8 to stay on the MIT line; gate ELv2 as opt-in
purpose: Records the decision to cap the kreuzberg dependency at the last MIT release and ship v4.8+ ELv2 behind an opt-in extra
created: 2026-05-25
updated: 2026-05-26
validated_links: 2026-05-26
category: technical
---

## Status

Accepted — 2026-05-26

## Context and Problem Statement

Kreuzberg is the breadth-catch-all extraction backend wired as the
`[extract]` extra in `pyproject.toml`. Until v4.7.x it shipped under
MIT. Starting v4.8, upstream relicensed to Elastic License v2 (ELv2),
a source-available licence that is not OSI-approved and prohibits
offering the software as a managed service without Elastic's consent.

GitHub's SPDX detector classifies ELv2 as `NOASSERTION`, so a casual
audit can miss the change. The relicensing surfaced via direct
LICENSE-file inspection (issue #76). The copyright holder also changed
at the same time (individual → Kreuzberg, Inc.), indicating the project
incorporated and pivoted to a source-available model in one move.

Our distribution stance is Apache-2.0; consumers (polyforge,
office-polyforge, any redistributor of doc-pipeline-engine) inherit our
dependency licence posture. An unbounded `kreuzberg>=2.0` pin means
`uv sync` on a fresh environment could resolve to v4.8+ and silently
pull in ELv2. Our `uv.lock` pin was already at v4.9.5 — already on
ELv2 — at the time of discovery.

## Decision Drivers

- Apache-2.0 distribution posture; ELv2 cannot be redistributed as
  Apache-2.0
- Embeddable-engine framing: downstream consumers must not inherit
  source-available constraints they didn't opt into
- Tier-G handling pattern already established in
  `docs/landscape/domain-extraction.md` for restricted licences
- Security backports for the MIT line become our responsibility once
  upstream moves to ELv2-only
- Kreuzberg's breadth (email, xlsx, legacy Office, HTML) is load-bearing
  for v1; replacing it wholesale is out of scope

## Considered Options

### Option 1 — Pin `kreuzberg<4.8` as the default; ship v4.8+ ELv2 behind an opt-in `[kreuzberg-elv2]` extra

- Good, because keeps the default install Apache-2.0-compatible
- Good, because preserves Kreuzberg's load-bearing breadth on the MIT line
- Good, because mirrors the Tier-G gating template already used for MinerU and PyMuPDF
- Good, because makes the licence choice explicit and downstream
- Bad, because we own security backports for the MIT line going forward
- Bad, because Python 3.14 wheels may eventually require v4.8+ (re-evaluate then)
- Bad, because extra to maintain

### Option 2 — Accept ELv2 as the default

- Good, because zero extra maintenance burden
- Good, because stays on the upstream-maintained line
- Bad, because bleeds ELv2 onto every consumer of `doc-pipeline-engine[extract]`
- Bad, because source-available constraint violates the Apache-2.0 distribution
  promise

### Option 3 — Replace Kreuzberg with docling for the catch-all role

- Good, because docling is MIT and already the planned Primary layout-aware backend
- Good, because removes a dependency
- Bad, because docling does not currently cover email, xlsx, legacy Office, or HTML
  to Kreuzberg's breadth; gaps would need bespoke adapters
- Bad, because out of scope for v1; wholesale extraction-stage rewrite

## Decision Outcome

Chosen: **Option 1**. Pin `kreuzberg<4.8` in `pyproject.toml`. Ship
v4.8+ as an opt-in `[kreuzberg-elv2]` extra so consumers who accept the
ELv2 constraint can opt in explicitly. Surface the thresholds and
attribution behaviour in `NOTICE`. PR #88 implements the pin.

Re-evaluate when: (a) Python 3.14 wheels require v4.8+, (b) a CVE
backport burden becomes unsustainable, or (c) docling's coverage
expands enough to absorb Kreuzberg's breadth niche.

## More Information

- Issue #76: <https://github.com/qte77/doc-pipeline-engine/issues/76>
- PR #88: <https://github.com/qte77/doc-pipeline-engine/pull/88>
- Tier G reference: [../landscape/domain-extraction.md#license-tier-reference](../landscape/domain-extraction.md#license-tier-reference)
- ELv2 text: <https://www.elastic.co/licensing/elastic-license>
- Kreuzberg releases: <https://github.com/kreuzberg-dev/kreuzberg/releases>
