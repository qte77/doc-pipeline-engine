### Added

- Landscape rows for `anydoc`, `Unstructured`, `MarkItDown`, `DeepSeek-OCR`, `Chandra`, `TurboOCR` and `dots.ocr` in [ingest.md](docs/landscape/ingest.md) §1; `gmft` (§2), `Microsoft GraphRAG` (§4) and `LangExtract` (§6) in [process.md](docs/landscape/process.md); `RAGFlow` in [e2e-systems.md](docs/landscape/e2e-systems.md) §2.
- `ContextGem` documented as a sibling of `instructor` and `GLiNER2` as a successor to the GLiNER/GLiREL/gliner-multitask trio, both in [process.md](docs/landscape/process.md) §3.
- Per-row `*(added YYYY-MM-DD)*` / `*(verified YYYY-MM-DD)*` markers across the three landscape files, so row-level fact staleness is visible independently of the file-level frontmatter date.
- ExtractBench ([arXiv:2607.29677](https://arxiv.org/abs/2607.29677)) as the first independent benchmark of NuExtract3, recorded in [process.md](docs/landscape/process.md) §6.

### Changed

- **marker licence corrected**: its own code relicensed GPL-3.0 → Apache-2.0 at v2.0.0 (2026-07-20); only the bundled OpenRAIL-M weights remain Tier-G gated. Updated in `ingest.md` §1, `process.md` §2 and the `e2e-systems.md` §5.3 licence-isolation claim.
- **Kreuzberg upstream moved**: `kreuzberg-dev/kreuzberg` now redirects to `xberg-io/xberg` (MIT, Rust core), with an MIT `kreuzberg-dev/kreuzberg-lts` for the v4 line past the v4.8 ELv2 cut. Recorded as an open question against [ADR-0005](docs/adr/0005-kreuzberg-elv2-license-boundary.md); the pin is unchanged pending a follow-up pass.
- **NuExtract3 verdict evidence**: ExtractBench measures 47.9% unified value-F1 overall, 8.9% on long documents and 3.7% on enormous tables — the `external/nuextract` benchmark should adopt those hard splits as its pass bar rather than NuMind's self-reported 0.651.
- Refreshed version, release-date and star figures across `ingest.md` and `process.md` (docling, PaddleOCR-VL, olmOCR, pdfplumber, MinerU, LibreOffice, LiteParse, crawl4ai, trafilatura, watchdog, ColPali, chonkie, Camelot, GLiNER, instructor, Flair, Haystack, LightRAG, nano-graphrag, outlines, docling-core). Corrected two wrong dates: watchdog v6.0.0 is 2024-11-01 (not 2026-05-07) and nano-graphrag v0.0.8 is 2024-10-01 (not 2026-01-27).
- Tempered the "competitor field has stalled" reading in `e2e-systems.md` §5.1 — RAGFlow is an active competitor at similar scope, so the embeddable-vs-service argument should not lean on competitor decay.

### Security

- `dots.ocr` recorded as **Avoid**: the repo ships two contradictory licence files (a 1 KB MIT `LICENSE` and a 15 KB `dots.ocr LICENSE AGREEMENT`) and `requirements.txt` hard-pulls AGPL-3.0 `PyMuPDF`, which would bleed into embedding consumers.
