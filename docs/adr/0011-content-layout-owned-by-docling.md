---
title: ADR-0011 — docling owns content.layout population (bbox + provenance)
purpose: Records that ExtractionBundle.content.layout is filled from docling (geometry + semantic kind + provenance), with pdfplumber as a born-digital cross-check, and that the external bbox parsers LiteParse and OmniParse are rejected
created: 2026-06-11
updated: 2026-06-11
validated_links: 2026-06-11
category: technical
---

## Status

Accepted — 2026-06-11

## Context and Problem Statement

`ExtractionBundle.content.layout` is a **required** `list[LayoutBlock]`
(`kind`, `page`, `bbox=[x0,y0,x1,y1]`, `level`, `text`;
`models/extraction_bundle.py`). The only wired adapter, Kreuzberg, emits
`layout: []` — a text-only stopgap (`stages/extract.py`).

This is not a cosmetic gap. `CanonicalDoc.Node.source_refs`
(`SourceRef.layout_index` + `page`; `models/canonical_doc.py`) indexes
**back into** `content.layout`. An empty layout therefore severs the
canonical-node → source-coordinate traceability the contract was built
around, and blocks the Comprehensive tier's tables/figures/citations.

A request to evaluate two external parsers — OmniParse and LiteParse —
triggered a wider extraction-backend sweep (also pdfplumber,
pdfminer.six, olmOCR; see [ingest.md §1](../landscape/ingest.md#1-extraction-backends)).
The question this ADR settles: **which backend populates
`content.layout`, and do we adopt an external bbox parser to do it?**

## Decision Drivers

- `content.layout` is the provenance backbone for `CanonicalDoc`
  (`source_refs`); it cannot stay empty for Comprehensive-tier output.
- `LayoutBlock` requires a **semantic `kind`**, not just geometry — the
  producer must classify blocks (heading/table/figure/…), not only
  locate them.
- Apache-2.0 distribution posture ([ADR-0006](0006-apache-2-0-with-notice-over-mit.md))
  and Python-native / `uv` footprint ([ADR-0008](0008-hatchling-and-uv-over-setuptools-and-pip.md)):
  non-Python runtimes and copyleft / NonCommercial licences must justify
  themselves (Tier reference in
  [domain-extraction.md](../landscape/domain-extraction.md#license-tier-reference)).
- docling is already the Primary layout-aware backend
  ([ingest.md §1](../landscape/ingest.md#1-extraction-backends)).

## Considered Options

### Option 1 — docling owns content.layout; pdfplumber as born-digital cross-check

- Good, because docling emits geometry **and** semantic `kind` **and**
  provenance together — the exact `LayoutBlock` + `source_refs` shape.
- Good, because docling is MIT (Tier A) and already the Primary backend;
  no new runtime is introduced.
- Good, because pdfplumber (MIT, pure-Python) gives a torch-free
  born-digital geometry/tables cross-check for §0.4.0.
- Bad, because pdfplumber alone cannot fill `kind` (no classifier).
- Bad, because docling pulls `torch`, and the `bbox` origin convention
  must be fixed before cross-adapter comparison is meaningful.

### Option 2 — adopt LiteParse for bbox

- Good, because it returns clean per-line bboxes out of the box (spike
  2026-06-11: 976 positioned items from a 15-page PDF in ~10.5 s).
- Good, because Apache-2.0 (Tier A).
- Bad, because the Python package subprocesses a **Node ≥18 CLI** —
  a non-Python runtime in a `uv`/Python install (against
  [ADR-0008](0008-hatchling-and-uv-over-setuptools-and-pip.md)).
- Bad, because OCR uses a bundled `tesseract-rs` that ignores the system
  Tesseract, and image/SVG input needs system ImageMagick.
- Bad, because it yields geometry + font but **not** semantic `kind`.
- Bad, because its only advantage (bbox) is already covered by
  docling + pdfplumber; run-llama themselves route hard documents to
  cloud LlamaParse.

### Option 3 — adopt OmniParse

- Good, because broad multi-modal coverage (PDF/Office/image/audio/
  video/web) into structured Markdown.
- Bad, because **GPL-3.0** code (Tier F) + **cc-by-nc-sa-4.0**
  NonCommercial weights (Tier E) — NC blocks commercial redistribution.
- Bad, because it needs an 8–10 GB GPU server (Docker/REST).
- Bad, because the audio/video/web breadth is out of scope for the
  document stages (YAGNI).

### Option 4 — leave content.layout empty (status quo)

- Good, because zero work.
- Bad, because it severs `CanonicalDoc.source_refs` provenance and keeps
  a required contract field dead, blocking Comprehensive-tier output.

## Decision Outcome

Chosen: **Option 1**. docling populates
`ExtractionBundle.content.layout` (geometry + semantic `kind` +
provenance). pdfplumber is an opt-in, pure-Python born-digital
cross-check (geometry/tables) for §0.4.0. Kreuzberg remains the breadth
catch-all, but its bundles stay text-only (`layout: []`) and are
**not** eligible to build a provenance-bearing `CanonicalDoc`.

Reject **LiteParse** (Option 2) and **OmniParse** (Option 3): the bbox
capability that motivated them is already available Python-natively from
docling, without a Node runtime or NonCommercial/GPL/GPU cost.

Two conventions to fix when wiring the docling adapter at
[§0.4.0](../roadmap.md#040--adapters):

1. **Coordinate origin** — `LayoutBlock.bbox` is documented as
   `[x0,y0,x1,y1] in page units` but the **origin is unspecified**. Fix
   it (recommended: top-left, y-down, page points) and normalize inside
   each adapter, or cross-adapter comparison and `source_refs` silently
   misalign.
2. **docling-label → `LayoutBlock.kind` map** — `section_header →
   heading` (+`level`), `text → paragraph`, `table → table`,
   `picture → figure`, `caption → caption`, `formula → formula`,
   `code → code`, `footnote → footnote`, `list_item → list` — plus
   reading-order ordering.

Re-evaluate when: docling's bbox fidelity proves insufficient on the
§0.4.0 cross-validation sample set, or a Python-native producer of both
geometry **and** semantic `kind` surpasses it.

## More Information

- Sweep + verdicts:
  [ingest.md §1 — Extraction backends](../landscape/ingest.md#1-extraction-backends)
- Licence Tier reference:
  [domain-extraction.md#license-tier-reference](../landscape/domain-extraction.md#license-tier-reference)
- Contract models: `src/doc_pipeline_engine/models/extraction_bundle.py`
  (`LayoutBlock`), `src/doc_pipeline_engine/models/canonical_doc.py`
  (`SourceRef`)
- Related: [ADR-0005](0005-kreuzberg-elv2-license-boundary.md) (Kreuzberg
  breadth role), [ADR-0006](0006-apache-2-0-with-notice-over-mit.md)
  (Apache-2.0 posture),
  [ADR-0008](0008-hatchling-and-uv-over-setuptools-and-pip.md)
  (Python-native / `uv`)
- LiteParse: <https://github.com/run-llama/liteparse>
- OmniParse: <https://github.com/adithya-s-k/omniparse>
- pdfplumber: <https://github.com/jsvine/pdfplumber>
- docling: <https://github.com/docling-project/docling>
