---
title: Local-leg example outputs
purpose: Reference summaries the offline local leg produces via make run_local on Python 3.13
created: 2026-06-22
updated: 2026-06-22
validated_links: 2026-06-22
category: implementation
---

Deterministic outputs of the offline `local` leg (`make run_local SAMPLE=…`) on
Python 3.13 with spaCy NER enabled. The leg is deterministic but un-tuned, so the
entity lists include some noise (numbers and heading fragments tagged `other`).
Reproduce with `make run_local`; full artifacts land in
`outputs/<sha>/local/{summary.md,docx,pdf}` (gitignored). The source files are
third-party content under various licenses — see [NOTICE](../../../NOTICE) and
[scripts/download-samples.sh](../../../scripts/download-samples.sh) for per-file
attribution. Only redistribution-clean sources (UK OGL / US Public Domain) are
excerpted here.

## uk-short-form-contract.docx — UK OGL v3.0

`sha256 88c177fe3a74…` · 13 claims · 669 entities

```markdown
## Key Claims

- 3How the Contract works18
- 6The Buyer's obligations to the Supplier21
- 12How much you can be held responsible for26

## Entities

- **New IPR** (org)
- **Contract** (org)
- **SUB-CONTRACTORS** (org)
```

## us-open-government-act-2007.pdf — US Public Domain

`sha256 3af32df1de87…` · 22 claims · 101 entities

```markdown
## Key Claims

- Public Law 110–175, 110th Congress — An Act to promote accessibility,
  accountability, and openness in Government by strengthening section 552 of
  title 5 (the Freedom of Information Act).

## Entities

- **Senate** (org)
- **House of Representatives** (org)
- **Congress** (org)
- **the United States of America** (location)
```

## nist-sp800-63b.pdf — US Public Domain

`sha256 ccfce7510a12…` · 105 claims · 680 entities

```markdown
## Key Claims

- Digital Identity Guidelines: Authentication and Authenticator Management
  (NIST SP 800-63B), David Temoshok et al.

## Entities

- **David Temoshok** (person)
- **July 2025** (measurement)
```
