---
title: ADR-0013 — pseudonymize-text as the default redactor for the cloud-redacted profile
purpose: Records the choice of pseudonymize-text over presidio-analyzer and philter as the default PII/PHI redactor between Extract and Analyze in the cloud-redacted profile
created: 2026-10-24
updated: 2026-10-24
validated_links: 2026-10-24
category: technical
---

## Status

Accepted — 2026-10-24 (decision recorded on
[#107](https://github.com/qte77/doc-pipeline-engine/issues/107); wiring deferred)

## Context and Problem Statement

The [§0.5.0](../roadmap.md#050--domain-packs) `cloud-redacted` data-locality
profile sends document text to a cloud model only after personal data is
removed. That needs a default redactor between Extract and Analyze. The
candidates are listed in
[domain-extraction.md § PHI / de-identification](../landscape/domain-extraction.md#phi--de-identification).

This is an ADR rather than a wiring detail because a reversible redactor keeps
a mapping (a stored PII surface even after redaction), the redactor becomes a
load-bearing dependency of every cloud profile, and its interface cuts across
stages.

## Decision Drivers

- Reversible, deterministic pseudonyms, so downstream consumers can re-identify
  under control of the key holder.
- Runs on the repo's Python 3.14 environments (spaCy has had no 3.14 wheels —
  see the `local-render` extra note in `pyproject.toml`).
- Permissive licence (compatible with [ADR-0006](0006-apache-2-0-with-notice-over-mit.md)).
- Works on extracted text: PDF/Office/image inputs reach the redactor only
  after Extract (and OCR for scans).

## Considered Options

### Option 1 — `pseudonymize-text` (qte77 sibling)

- Good, because HMAC-SHA256 pseudonyms are deterministic and reversible; the
  mapping file is kept separate from both the output and the key.
- Good, because it is Apache-2.0, `requires-python >=3.11`, and spaCy is only
  an optional `[ner]` extra — the default install is 3.14-clean.
- Good, because the audit-first `detect` → `apply` flow fits a gated stage.
- Bad, because it is young (v0.2.0 at decision time) and narrower in entity
  coverage than presidio.

### Option 2 — `presidio-analyzer` (Microsoft, MIT)

- Good, because it has the widest entity coverage and broad adoption.
- Bad, because it depends on spaCy, which collides with the 3.14 split.
- Bad, because reversibility needs the separate `presidio-anonymizer`.

### Option 3 — `philter` (UCSF, BSD-3-Clause)

- Good, because it targets HIPAA Safe Harbor for clinical notes.
- Bad, because it strips data (not reversible) and is clinical-note specific.

## Decision Outcome

Chosen: **Option 1 — `pseudonymize-text`**, decided at v0.2.0. The earlier
"v0.0.2 (Planning); pin until ≥0.1" framing is obsolete: the ≥0.1 guard is
already met (v0.3.0 is the latest release as of 2026-10-24).
`presidio-analyzer` stays a documented opt-in alternative for `<3.14`
environments; `philter` is not adopted.

Interface constraints carried into the wiring work:

- Stage order: `Discover → Extract → Pseudonymize → Normalize → Analyze`. The
  redactor reads `ExtractionBundle` text fields, not raw bytes; scanned PDFs
  and images pass through OCR first.
- Contract shape: text in, redacted text out; the mapping handle is exposed
  separately from the data stream.
- Mapping and key stay outside the bundle and outside `runs/`.
- Pin `pseudonymize-text>=0.2,<1` when the extra lands.

### Deferred

Per #107's "do not pre-wire" gate, these land with the §0.5.0
`cloud-redacted` profile, not with this ADR: the `Redactor` contract in
`src/doc_pipeline_engine/models/`, a `stages/redact_*.py` stage, the
`[redact]` extra, and the "de-identification (pre-NER)" subsection in
`docs/landscape/process.md` §3. Rebuilding a redacted PDF with its layout
stays a roadmap Future item.

## More Information

- Decision thread: <https://github.com/qte77/doc-pipeline-engine/issues/107>
- pseudonymize-text: <https://github.com/qte77/pseudonymize-text>
- presidio: <https://github.com/microsoft/presidio>
- philter: <https://github.com/BCHSI/philter-ucsf>
- Related: [ADR-0005](0005-kreuzberg-elv2-license-boundary.md) (licence boundary pattern)
