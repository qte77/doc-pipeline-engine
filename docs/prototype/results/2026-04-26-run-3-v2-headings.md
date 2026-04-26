---
title: Prototype run 3 — V2 heading-tree reconstruction
purpose: V2-only re-run on the five locked samples after v2_normalize learns heading detection (issue #33)
created: 2026-04-26
updated: 2026-04-26
validated_links: 2026-04-26
category: implementation
---

Third harness run, executed 2026-04-26. V2 leg only — V1 unchanged
since [run 2](2026-04-26-run-2-v1-cli.md), so re-running the cloud leg
adds no signal. The single change since run 2 is
[#33](https://github.com/qte77/doc-pipeline-engine/issues/33):
`v2_normalize` now reconstructs a flat heading tree from heuristic
detection over the Kreuzberg-extracted plain text instead of wrapping
the entire document in one leaf section.

## Per-sample axes (V2 only)

| Use case | sha (head) | extract chars | V2 wall (s) | sections | claims (run 2 → run 3) | V2 md chars (run 2 → run 3) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Contract (DOCX) | `88c177fe3a74` | 219,840 | 1.92 | 69 | 1 → 13 | 3,600 → 1,467 |
| Legal (PDF) | `3af32df1de87` | 21,818 | 0.23 | 24 | 1 → 22 | 59 → 8,295 |
| Invoice (PDF) | `bedf3200fa3c` | 5,228 | 0.09 | 1 | 1 → 1 | 66 → 66 |
| Spec (PDF) | `1df8d26a8bd7` | 57,174 | 0.59 | 134 | 1 → 98 | 318 → 20,128 |
| Diagram (JPG) | `8a799b15d781` | 0 | 0.07 | 1 | 1 → 1 | 59 → 59 |

V2 stages still finish well under one second per sample on the
text-bearing inputs. Rendered md/docx/pdf artifacts under
`outputs/<sample_sha256>/v2/`.

## What changed

`v2_normalize` now runs three regex families against each line of the
extracted text:

- formal-prefix headings (`SECTION 1.`, `SEC. 2.`, `CHAPTER`, `ARTICLE`,
  `PART`) — the legal sample's primary structure;
- numbered with space (`1 Features`, `5.1 Specs`, `6.3.1 Monostable
  Operation`) — the spec datasheet's primary structure;
- numbered glued (`1Definitions`, `2Understanding`) — the contract DOCX's
  ToC-flatten artifact.

Detected heading lines become section boundaries; level is the
dot-count of the numeric prefix (`5` → 1, `5.1` → 2, capped at 6 per
the schema). Two fallbacks preserve the run-2 single-leaf shape: zero
detected headings (invoice, diagram), and detected density above 50%
of non-empty lines (none of the five samples tripped this in practice;
the contract was the suspected case but its 69 headings sit inside
220K chars of body, so density stays well below the cap).

## Content delta

Concrete claim-count delta on the spec sample, which gained the most
structure:

- **run 2**: `Quick Summary / Key Claims / - timer features (1 bullet)`
- **run 3**: 98 bullets, each the first sentence of one detected
  section ("1 Features", "2 Applications", "5.1 Specs", …).

Concrete claim-count delta on the legal sample:

- **run 2**: 1 bullet (`Public Law 110-175 …`).
- **run 3**: 22 bullets, one per `SECTION`/`SEC.` boundary in the
  OPEN Government Act of 2007. The first bullet is the public-law
  preamble; subsequent bullets are the short titles + first sentence
  of each enumerated section.

The contract V2 markdown actually shrinks from 3,600 → 1,467 chars
because we now emit one bullet per detected section rather than the
entire 220K-char body as one bullet's first sentence (the run-2
behavior took the first sentence of the whole document, but the
Jinja render's bullet-per-claim path produced a longer single bullet
for a different code path; with 13 substantive claims the bullets are
shorter and more focused).

## Faithfulness gaps and surprises

1. **Invoice and diagram correctly stay at 1 claim.** Neither has
   detectable headings — the invoice is a form, the diagram has no
   OCR-readable text. Both fall back to the run-2 single-leaf shape.
   No false positives, no hallucinated structure.

2. **Bullet quality is "first sentence of section body", not section
   title.** `v2_analyze._extract_claims` was unchanged (per the plan's
   reuse principle). For the run-3 markdown, this means each bullet is
   the first sentence following the heading, not the heading itself.
   Section titles are stored in `canonical.root.children[i].title` and
   are available to a future render template upgrade.

3. **No render-template change.** The Jinja template at
   `stages/_jinja_templates/quick_summary.md.j2` still iterates claims
   as flat bullets. Promoting section titles into `##` subheadings is
   a render-side polish deferred from #33.

4. **`tier_summary` still head-of-text.** `l0`/`l1` are unchanged
   first-200 / first-1000 char excerpts of the raw extracted text.
   Heading-aware tier summaries (titles + first sentences) are an
   easy follow-up but out of #33's scope.

## Open follow-ups (still standing after this run)

- **Real nested hierarchy** — section levels are recorded
  (`level=1/2/3`) but the tree is flat (all children of `root`). A
  stack-based builder would nest level-2 under level-1 etc. Tracked
  as a follow-up to #33.
- **Render template upgrade** — emit section titles as `##`
  subheadings; would make V2 markdown structurally readable rather
  than a long bullet list.
- **Heading-aware `tier_summary`** — replace head-of-text truncation
  with title + first-sentence digest.
- **`extract.py` switch to `include_document_structure=True`** —
  would give Kreuzberg-pre-chunked nodes (36 for NE555) for free, but
  changes the `ExtractionBundle` shape and V1 prompts. Separate,
  larger PR.
- **Backend marker in `EvalReport`** (carried over from run 2) —
  record V1 backend (SDK vs CLI) + `total_cost_usd` from the CLI
  envelope.
- **Cross-repo follow-up** —
  [`qte77/gha-llms-txt-action#6`](https://github.com/qte77/gha-llms-txt-action/issues/6).
