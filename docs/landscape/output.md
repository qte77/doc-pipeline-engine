---
title: Output Landscape
purpose: Survey of rendering, office formats, templating, and conformance validators for the output stage
created: 2026-04-26
updated: 2026-05-25
validated_links: 2026-05-25
category: landscape
---

Survey of candidates for the **output** stage — rendering, office formats, templating, and `OutputFormat` / `FormatConformance` validators. Companion files: [ingest.md](ingest.md), [process.md](process.md), [e2e-systems.md](e2e-systems.md), [domain-extraction.md](domain-extraction.md).

Output emits documents validating against `OutputFormat` (`id`, `version`, `tier`) and `FormatConformance` (`output_format_id`, `conformant`). Tiers from [architecture.md](../architecture.md):

- **Quick** — 1-page Markdown summary
- **Comprehensive** — IMRaD / tech-spec; full canonical tree + tables/figures/citations

## Selection criteria

1. **License compatibility** — Apache-2.0 friendly; AGPL/GPL opt-in only. Pandoc is GPL-2.0-or-later (subprocess pattern is the standard mitigation).
2. **Runtime footprint** — Python-native preferred; external binary / JVM must justify itself.
3. **Output coverage** — Markdown, DOCX, PDF, PPTX, HTML, LaTeX, Typst.
4. **Template ergonomics** — how cleanly `CanonicalDoc` trees drive output.
5. **Maintenance signal** — active releases, non-trivial user base.

## 1. Rendering engines

| Tool | License | Runtime | Output formats | Verdict |
| --- | --- | --- | --- | --- |
| **WeasyPrint** ([repo](https://github.com/Kozea/WeasyPrint)) | BSD-3-Clause | Python-native | PDF, PNG (from HTML/CSS) | **Primary (PDF)** — v68.1 (2026-05-25), 9k stars. Pure-Python HTML→PDF; good CSS3 support; no Haskell/Rust install. |
| **ReportLab** | BSD-3-Clause / commercial (RLPDF) | Python-native | PDF | **Primary (programmatic PDF)** — battle-tested; preferred for data-heavy tables and charts in Comprehensive. |
| **Typst** ([repo](https://github.com/typst/typst)) | Apache-2.0 | External binary (Rust); `typst` Python binding | PDF, PNG, SVG | **Optional** — v0.14.2 (2026-05-25), 54k stars. Modern TeX replacement; Python binding removes shell-out. |
| **Pandoc** ([repo](https://github.com/jgm/pandoc)) | **GPL-2.0-or-later** | External binary (Haskell) | MD, DOCX, PDF (LaTeX/Typst), HTML, EPUB, LaTeX, RST, … | **Optional** — v3.9.0.2 (2026-05), 44k stars. Broadest converter; subprocess use does not impose GPL on the caller, but ship behind `[pandoc]` extra to make the choice explicit. |
| **Quarto** ([repo](https://github.com/quarto-dev/quarto-cli)) | MIT (COPYING.md; GitHub API returns NOASSERTION) | External binary (Deno + Pandoc) | HTML, PDF, DOCX, PPTX, EPUB | **Optional** — v1.9.38 (2026-05-25), 6k stars. Best for IMRaD/science reports; heavy install; transitive Pandoc concern. |
| **Sphinx** ([repo](https://github.com/sphinx-doc/sphinx)) | BSD-2-Clause (LICENSE.rst; GitHub API returns NOASSERTION) | Python-native (LaTeX for PDF) | HTML, PDF, EPUB, man | **Optional** — 8k stars. Autodoc/tech-spec output; heavy for single-doc use. |
| **mdBook** ([repo](https://github.com/rust-lang/mdBook)) | MPL-2.0 | External binary (Rust) | HTML book, PDF (via print) | **Optional** — 22k stars. Multi-chapter docs sites; MPL-2.0 file-scoped copyleft, acceptable as subprocess. |

**Notes** — WeasyPrint + ReportLab cover the two Python-native PDF paths and form the default for Comprehensive PDF. Typst is the cleanest binary path for production-quality PDFs. Pandoc is the Swiss-army-knife behind a license gate.

## 2. Office formats (write side)

| Tool | License | Runtime | Formats | Verdict |
| --- | --- | --- | --- | --- |
| **python-docx** ([repo](https://github.com/python-openxml/python-docx)) | MIT | Python-native | DOCX | **Primary** — 6k stars, last push 2025-06-17. Standard DOCX writer; first-class `CanonicalDoc → DOCX` adapter target. |
| **docxtpl** ([repo](https://github.com/elapouya/python-docx-template)) | LGPL-2.1 | Python-native (wraps python-docx) | DOCX | **Primary (templates)** — 3k stars, last push 2026-05-18. Jinja2-in-DOCX; LGPL is library-use safe for Apache-2.0 callers when not modifying the lib. Confirm with legal before redistributing modified copies. |
| **python-pptx** ([repo](https://github.com/scanny/python-pptx)) | MIT | Python-native | PPTX | **Primary** — 3k stars, last push 2024-08-07. Only serious Python PPTX writer. |
| **openpyxl** | MIT | Python-native | XLSX (read+write) | **Primary** — standard XLSX writer; required for tabular outputs. |
| **xlsxwriter** ([repo](https://github.com/jmcnamara/XlsxWriter)) | BSD-2-Clause | Python-native | XLSX (write only) | **Secondary** — 4k stars, last push 2026-03-22. Richer chart/formatting API; use when output requires complex Excel charts. |
| **odfpy** ([repo](https://github.com/eea/odfpy)) | Apache-2.0 / GPL-2.0 (dual; LICENSE files confirm both — API reports NOASSERTION) | Python-native | ODS, ODT, ODP | **Optional** — 357 stars, last push 2026-04-07. ODF rarely required by primary consumers. Note: prior entry listed LGPL-2.1 incorrectly; repo contains `APACHE-LICENSE-2.0.txt` and `GPL-LICENSE-2.txt`. |

## 3. Templating engines

| Tool | License | Runtime | Use case | Verdict |
| --- | --- | --- | --- | --- |
| **Jinja2** ([repo](https://github.com/pallets/jinja)) | BSD-3-Clause | Python-native | HTML, MD, LaTeX, Typst text templates | **Primary** — v3.1.6 (2025-06-14), 11k stars. De-facto standard; covers Quick and Comprehensive text templates. |
| **pystache** | MIT | Python-native | Mustache logic-less templates | **Optional** — pick where logic-less is required for cross-language template sharing. |
| **chevron** | MIT | Python-native | Mustache | **Avoid** — last push 2023-08-24, no releases; prefer pystache. |
| **mjml-python** | MIT | Python-native (transpiler port) | Responsive HTML email | **Optional** — gate behind `[email]` extra. |

**Notes** — Jinja2 is the only must-have. Pick one Mustache impl (pystache) if needed; don't ship both.

## 4. Output-format conformance / validators

Backs the `FormatConformance` contract. Practical pattern: rely on writer libraries for structural correctness in the hot path, delegate strict format validators (PDF/A, HTML5) to CI or opt-in extras.

| Tool | License | Runtime | Validates | Role |
| --- | --- | --- | --- | --- |
| **python-docx structural check** | MIT | Python-native | DOCX (OOXML constructor raises on malformed) | **Runtime** — pair with `lxml` schema validation for deeper checks. |
| **WeasyPrint runtime errors** | BSD-3-Clause | Python-native | HTML/CSS for PDF rendering | **Runtime** — raises on unrenderable input. |
| **pymarkdownlnt** ([repo](https://github.com/jackdewinter/pymarkdown)) | MIT | Python-native | CommonMark / GFM Markdown | **Runtime** — v0.9.37 (2026-05-19), 136 stars. Backs Quick-tier Markdown conformance. |
| **markdownlint-cli2** ([repo](https://github.com/DavidAnson/markdownlint-cli2)) | MIT | Node.js | Markdown | **CI gate** — 815 stars, last push 2026-05-21. Richer ruleset; only if Node already present. |
| **veraPDF** ([repo](https://github.com/veraPDF/veraPDF-library)) | GPL-3.0 + MPL-2.0 (dual) | **JVM** | PDF/A-1b/2b/3b/u, PDF/UA | **Optional / CI-only** — v1.30.1 (2026-05-19), 330 stars. Best PDF/A validator; JVM dep. Gate behind `[pdf-a]` or run only in CI. |
| **vnu (Nu HTML Checker)** | MIT | **JVM** | HTML5 | **Optional / CI-only** — same opt-in pattern as veraPDF. |
| **htmlhint** ([repo](https://github.com/HTMLHint/HTMLHint)) | MIT | Node.js | HTML lint | **CI gate** — 3k stars, last push 2026-05-21. Lighter than vnu. |
| **mammoth** ([repo](https://github.com/mwilliamson/python-mammoth)) (read-side) | BSD-2-Clause | Python-native | DOCX semantic round-trip | **Optional** — 1k stars, last push 2026-05-24. Semantic-issue signal, not strict schema validation. |

**Notes** — There is no Python-native PDF/A validator. veraPDF (JVM) is the only production-grade option; don't embed in the runtime hot path.

## Recommended defaults vs. opt-in extras

| Tier | Default (no extra) | Opt-in extra |
| --- | --- | --- |
| PDF | WeasyPrint, ReportLab | Pandoc (`[pandoc]`), Typst (`[typst]`), Quarto (`[quarto]`) |
| DOCX | python-docx, docxtpl | — |
| XLSX/PPTX | openpyxl, python-pptx | xlsxwriter, odfpy |
| Templating | Jinja2 | pystache, mjml-python (`[email]`) |
| Conformance (runtime) | pymarkdownlnt, python-docx OOXML check | veraPDF (`[pdf-a]`), vnu / htmlhint (CI only) |

## See also

- [ai-agents-research / CC-office-document-skills.md](https://github.com/qte77/ai-agents-research/blob/main/docs/cc-native/plugins-ecosystem/CC-office-document-skills.md) — how Claude Code itself handles office documents at the orchestration layer (Anthropic's `/v1/skills` API for docx/xlsx/pptx/pdf). Complementary view: this file covers the engine-layer Python libraries; the linked file covers the CC integration layer above them.
- [../prototype/plan.md](../prototype/plan.md) — how the rendering and office-format candidates surveyed here get exercised in the v1 dual-variant prototype.

## Open questions

- Should `FormatConformance` for PDF be advisory (warn) or blocking (raise) at runtime, given veraPDF's JVM cost?
- Is PDF/A-2b the target archival profile, or is standard PDF sufficient for Quick tier?
- Confirm `docxtpl` LGPL-2.1 posture with project legal before treating as non-optional dep.
- chevron is unmaintained — standardise on pystache or drop Mustache entirely if Jinja2 covers all internal templates.
- Pandoc subprocess vs `[pandoc]` extra: same governance question as the process-stage Pandoc AST normalizer.

## References

### Rendering engines

- WeasyPrint: <https://github.com/Kozea/WeasyPrint>
- ReportLab: <https://www.reportlab.com/>
- Typst: <https://github.com/typst/typst>
- Pandoc: <https://github.com/jgm/pandoc>
- Quarto: <https://github.com/quarto-dev/quarto-cli>
- Sphinx: <https://github.com/sphinx-doc/sphinx>
- mdBook: <https://github.com/rust-lang/mdBook>

### Office formats

- python-docx: <https://github.com/python-openxml/python-docx>
- docxtpl: <https://github.com/elapouya/python-docx-template>
- python-pptx: <https://github.com/scanny/python-pptx>
- openpyxl: <https://foss.heptapod.net/openpyxl/openpyxl>
- xlsxwriter: <https://github.com/jmcnamara/XlsxWriter>
- odfpy: <https://github.com/eea/odfpy>

### Templating

- Jinja2: <https://github.com/pallets/jinja>
- pystache: <https://github.com/PennyDreadfulMTG/pystache>
- mjml-python: <https://pypi.org/project/mjml-python/>

### Conformance / validators

- pymarkdownlnt: <https://github.com/jackdewinter/pymarkdown>
- markdownlint-cli2: <https://github.com/DavidAnson/markdownlint-cli2>
- veraPDF: <https://github.com/veraPDF/veraPDF-library>
- vnu: <https://github.com/validator/validator>
- htmlhint: <https://github.com/HTMLHint/HTMLHint>
- mammoth: <https://github.com/mwilliamson/python-mammoth>
