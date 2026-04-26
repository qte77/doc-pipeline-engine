# Extraction Backend Landscape

Survey of candidate extraction backends for the `ExtractionBundle` stage (roadmap §0.4.0). Scope is limited to tools we would wire as **adapters** behind `base/adapter.py` — not a general OCR/PDF market scan.

## Selection criteria

1. **License compatibility** — must not force Apache-2.0 consumers into copyleft obligations. AGPL/GPL tools are optional-only.
2. **Format coverage** — PDF (born-digital + scanned), Office (docx/pptx/xlsx), images, HTML, email.
3. **Runtime footprint** — Python-native preferred; JVM/heavy native deps must justify themselves.
4. **Layout fidelity** — does it preserve headings, tables, reading order? (Required for `CanonicalDoc`.)
5. **OCR quality** — for scanned PDFs and images.
6. **Maintenance signal** — active releases, non-trivial user base.

## Candidates

| Tool | Primary role | License | Runtime | Formats | Verdict |
|---|---|---|---|---|---|
| **docling** | Layout-aware PDF/Office → structured doc | MIT | Python + torch | PDF, DOCX, PPTX, HTML, images | **Primary** — best layout fidelity, native target for `CanonicalDoc`. |
| **Kreuzberg** | Async multi-format extraction facade | MIT | Python (pypdfium2, Tesseract, python-docx, …) | PDF, Office, images, email, HTML | **Primary (breadth)** — covers the long tail with one adapter. |
| **claude_cli_adapter** | LLM-based extraction via Claude Code CLI | n/a (our code) | Claude CLI | Any (LLM-mediated) | **Primary (reference)** — end-to-end wired first; cross-validation baseline. |
| **GLM-OCR** | Vision-LLM OCR for complex scans | Apache-2.0 | GPU preferred | Images, scanned PDF | Stub adapter — specialized scan/handwriting path. |
| **PaddleOCR-VL** | Vision-LLM OCR, CJK-strong | Apache-2.0 | GPU preferred | Images, scanned PDF | Stub adapter — non-Latin script fallback. |
| **Tesseract** | Classical OCR engine | Apache-2.0 | Native C++ binary | Images, scanned PDF | **Transitive** — reached via Kreuzberg/docling; baseline OCR floor, not a direct adapter. |
| **PyMuPDF (fitz)** | Fast PDF text + layout + images | **AGPL-3.0** (or commercial) | Python + native | PDF | **Optional only** — best-in-class for born-digital PDFs, but AGPL would bleed into consumers. Ship behind an opt-in extra. |
| **Apache Tika** | Broad content-extraction server | Apache-2.0 | **JVM** | ~1000+ formats | **Optional (server-mode)** — JVM dep too heavy as default; useful as a remote adapter for enterprise consumers with existing Tika infra. |

## Notes

**docling vs Kreuzberg** — not redundant. docling is the layout-accurate path for PDFs that feed `CanonicalDoc`; Kreuzberg is the pragmatic catch-all for the formats docling doesn't handle well (email, xlsx, legacy Office). Run them side by side in 0.4.0 cross-validation.

**Tesseract positioning** — don't expose as its own adapter. It's a dependency of the Python wrappers; surfacing it separately would duplicate configuration surface for no gain.

**PyMuPDF license risk** — AGPL triggers on *distribution* of derived works. Because consumers (polyforge, office-polyforge) embed us, an AGPL hard dep would force them to AGPL as well. Keep it behind `pip install doc-pipeline-engine[pymupdf]` so the choice is explicit and downstream.

**Tika cost/benefit** — once you need a JVM, operations teams notice. Ship as a remote-server adapter (`tika.url=...`) rather than an embedded dep, so Java stays out of our install footprint.

## Open questions

- Do we need handwriting OCR in scope for 0.4.0, or defer with GLM-OCR? → see AGENT_REQUESTS.md if raised.
- Adapter registry policy: first-match, ensemble, or declared per-domain? → revisit during 0.5.0 domain packs.
- Minimum cross-validation set: which adapters must agree on which sample categories to call extraction "verified"?

## References

- docling: https://github.com/docling-project/docling
- Kreuzberg: https://github.com/kreuzberg-dev/kreuzberg
- GLM-OCR: https://github.com/THUDM/GLM-4 (OCR variant)
- PaddleOCR-VL: https://github.com/PaddlePaddle/PaddleOCR
- Tesseract: https://github.com/tesseract-ocr/tesseract
- PyMuPDF: https://github.com/pymupdf/PyMuPDF
- Apache Tika: https://tika.apache.org/
