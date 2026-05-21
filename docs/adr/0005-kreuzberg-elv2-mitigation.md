---
title: ADR-0005 — Kreuzberg ELv2 mitigation
purpose: Records the decision to pin the `extract` extra to the last MIT release of Kreuzberg (v4.7.4) and gate the ELv2 line behind an opt-in extra, with docling as the documented fallback path if v4.7.4 quality regresses
created: 2026-05-21
updated: 2026-05-21
validated_links: 2026-05-21
category: technical
---

**Status**: Proposed (pending v4.7.4 DOCX verification — see Verification below)

## Context

Kreuzberg upstream relicensed from MIT to Elastic License 2.0 (ELv2) on 2026-04-08 (commit `5bfd393`). The first ELv2 release is v4.8.0 (7 minutes after the licence-change commit). The pinned version in `uv.lock` at the time of decision is v4.9.5 — **already on ELv2**.

ELv2 is source-available but not OSI-open-source. It prohibits:

1. Offering the software (or derivatives) as a managed/hosted service to third parties.
2. Removing or altering licence / copyright / attribution notices.
3. Asserting patent claims against the licensor (terminates the licence).

This directly conflicts with the project's own positioning:

- [`docs/landscape/ingest.md`](../landscape/ingest.md) selection criterion #1: *"License compatibility — must not force Apache-2.0 consumers into copyleft obligations. AGPL/GPL tools are optional-only."* ELv2 is not copyleft but is more restrictive than the criterion allows for a default dep.
- [`docs/landscape/e2e-systems.md`](../landscape/e2e-systems.md) §5 gap-analysis claim #3: *"Strict license isolation — Apache-2.0 default."*

Downstream consumers (polyforge, office-polyforge, qte77 fleet) ship with `--extra extract` and would inherit ELv2 restrictions through Kreuzberg. The embeddable-engine USP fails for any consumer that wants to offer the result as a managed service.

## Decision

Pin the `extract` extra to `kreuzberg>=2.0,<4.8` (MIT line, frozen at v4.7.4). Add a new `kreuzberg-elv2` opt-in extra (`kreuzberg>=4.8`) for downstream consumers who explicitly accept ELv2. Pattern mirrors the existing PyMuPDF (AGPL) and Apache Tika (JVM) opt-in gates.

The default install path stays Apache-2.0-clean. Opt-in is one-line and documented.

## Verification gate (before this ADR moves to Accepted)

Discussion [#375](https://github.com/kreuzberg-dev/kreuzberg/discussions/375) upstream reports DOCX heading detection broken in v4.x. The `chore/v5-prep` branch has commit `d2f5d47413 fix(docx): restore markdown formatting markers` — meaning upstream acknowledges the regression. **Unknown:** whether v4.7.4 (the pin target) has the regression or whether it was introduced later in the v4.x line.

Before merging this ADR, verify v4.7.4 DOCX heading parity against the project's `samples/*.docx` corpus. Procedure (run outside the sandbox):

```bash
# Two isolated venvs, one per version.
uv venv /tmp/k-mit  && /tmp/k-mit/bin/pip install 'kreuzberg==4.7.4'
uv venv /tmp/k-elv2 && /tmp/k-elv2/bin/pip install 'kreuzberg==4.9.5'

SAMPLE=samples/<category>/<your-docx-file>.docx

for ver in /tmp/k-mit /tmp/k-elv2; do
  $ver/bin/python -c "
import asyncio, sys
from kreuzberg import extract_file
async def main(p):
    r = await extract_file(p)
    print(r.content)
asyncio.run(main(sys.argv[1]))
" $SAMPLE > $(basename $ver).txt
done

# Heading-marker measurement (regex families from local_normalize).
python -c "
import re, pathlib
patterns = {
  'formal':    r'^(?:SECTION|SEC\\.|CHAPTER|ARTICLE|PART)\\s+[\\dIVXLCM]+',
  'numbered':  r'^\\d+(?:\\.\\d+)*\\s+\\S',
  'glued':     r'^\\d+(?:\\.\\d+)*[A-Z][a-z]',
  'markdown':  r'^#{1,6}\\s+\\S',
}
for f in ('k-mit.txt', 'k-elv2.txt'):
    t = pathlib.Path(f).read_text()
    print(f, {n: len(re.findall(p, t, flags=re.M)) for n,p in patterns.items()})
"
```

**Interpretation:**

- v4.7.4 shows ≥5 matches AND v4.9.5 ≈ 0 → regression at v4.8; pin is a clean win. **Move ADR to Accepted.**
- Both versions show ≥5 matches → pin is still a win on locality (MIT) but DOCX quality isn't the deciding factor. **Move ADR to Accepted.**
- Both ≈ 0 → regression predates v4.7.4. **This ADR is wrong-headed.** Close this PR and start the Option B follow-up: switch `Extract` primary to docling, demote Kreuzberg to long-tail fallback only.

## Rejected alternatives

- **Accept ELv2 at v4.8+**: kills the load-bearing license-isolation USP (`e2e-systems.md` §5 claim #3). Even for non-SaaS downstream consumers, the licence creates audit and notice obligations that contradict the project's "Apache-2.0 default, no compliance overhead" promise.
- **Drop Kreuzberg, switch to docling unconditionally**: viable but loses the long-tail format coverage (email, legacy Office, broad image OCR). Documented as the conditional fallback if v4.7.4 verification fails (see above).
- **Request upstream to publish a `kreuzberg-mit` slim package**: refuted by precedent. Five-of-five comparable license pivots (Elasticsearch 2021, MongoDB 2018, Redis 2024, Terraform 2023, Sentry 2019) had *zero* cases of upstream publishing a permissive slim subpackage. The community response in every case was external fork (OpenSearch, OpenTofu, Valkey) or downstream acceptance, never upstream split. Goldziher's Discussion [#842](https://github.com/kreuzberg-dev/kreuzberg/discussions/842) explicitly invokes Elasticsearch as the analogy, signalling conscious adoption of that model. Filing the request would burn an issue slot and signal naïveté.
- **Fork v4.7.4 as a long-term `kreuzberg-mit` maintained externally**: the closest non-upstream version of the "publish slim package" idea. Defensible but expensive — would require ongoing security fixes against a frozen base. Defer until evidence of community gravity (≥10 downstream consumers requesting it). Not a v0.1.x decision.

## Consequences

- **v4.7.4 is frozen.** No upstream security fixes will arrive on the MIT line. Periodic `pip-audit` / Dependabot review of v4.7.4's own transitive deps required.
- **Default install path is Apache-2.0-clean.** Downstream consumers (polyforge, office-polyforge) gain explicit licence-isolation guarantees.
- **`uv.lock` regeneration required** — run `uv lock --upgrade-package kreuzberg` after this PR merges; current pin (`4.9.5`) violates the new constraint.
- **CHANGELOG entry under `### Security`** rather than `### Changed` — the relicense is a security-policy concern from the embeddable-engine USP perspective, not a feature tweak.
- **§0.5.0 domain packs unblocked** — `med-research-patents` and `mech-elec-cert` consumers can ship without the ELv2 audit overhead.
- **Track `chore/v5-prep` upstream.** If v5 ships with materially better DOCX/email *under ELv2*, the calculus may shift — re-evaluate in a future ADR.
- **Verification result must be appended** to this ADR before moving to Accepted (or the PR closed if verification fails).

## Sources

- Kreuzberg LICENSE migration commit: <https://github.com/kreuzberg-dev/kreuzberg/commit/5bfd393>
- Elastic License 2.0 text: <https://www.elastic.co/licensing/elastic-license>
- Issue [#76](https://github.com/qte77/doc-pipeline-engine/issues/76) — the originating critical issue.
- Discussion #375 upstream (DOCX heading regression): <https://github.com/kreuzberg-dev/kreuzberg/discussions/375>
- Discussion #842 upstream (Goldziher on ELv2 rationale): <https://github.com/kreuzberg-dev/kreuzberg/discussions/842>
- Precedent table (relicense pivots that did NOT publish permissive slim subpackages): Elasticsearch (SSPL/ELv2 2021-01) — <https://github.com/opensearch-project/OpenSearch>; MongoDB (SSPL 2018-10); Redis (RSALv2/SSPLv1 2024-03) — <https://github.com/valkey-io/valkey>; HashiCorp Terraform (BUSL 2023-08) — <https://github.com/opentofu/opentofu>; Sentry (BSL 2019-10).
- [`docs/landscape/ingest.md`](../landscape/ingest.md) Kreuzberg row + Notes block.
- [`docs/landscape/domain-extraction.md`](../landscape/domain-extraction.md) License-tier reference (tier G — Undeclared / NOASSERTION) cites the Kreuzberg case as motivation.
