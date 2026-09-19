---
title: Ingest Landscape
purpose: Survey of extraction backends, source connectors, and crawling/discovery providers for the ingest stage
created: 2026-04-26
updated: 2026-08-09
validated_links: 2026-08-09
category: landscape
---

Survey of candidates for the **ingest** stage — extraction backends, source connectors, and crawling/discovery providers. Companion files: [process.md](process.md), [output.md](output.md), [e2e-systems.md](e2e-systems.md), [domain-extraction.md](domain-extraction.md).

Rows carry a trailing `*(added YYYY-MM-DD)*` or `*(verified YYYY-MM-DD)*` marker recording when that row's version, star-count, and licence facts were last checked against first-party sources. The frontmatter date covers the file; these cover the individual row. A row with no marker predates the convention and should be treated as unverified since the frontmatter `updated` date.

## Selection criteria

1. **License compatibility** — must not force Apache-2.0 consumers into copyleft obligations. AGPL/GPL tools are optional-only.
2. **Format coverage / source coverage** — what the tool actually reaches.
3. **Runtime footprint** — Python-native preferred; JVM/heavy native deps must justify themselves.
4. **Auth/credential model** — for source connectors, must support OAuth 2.0 / service-account flows.
5. **Data-locality fit** — note cloud-only paths; relevant to [§0.5.0](../roadmap.md#050--domain-packs) `local-only` / `claude-api-extracted-only` / `cloud-redacted` policies.
6. **Maintenance signal** — active releases, non-trivial user base.

## 1. Extraction backends

Wired as adapters behind `base/adapter.py`. Emit `ExtractionBundle`.

| Tool | Primary role | License | Runtime | Formats | Verdict |
| --- | --- | --- | --- | --- | --- |
| **docling** | Layout-aware PDF/Office → structured doc; native VLM pipeline (Granite Vision 4.1) added v2.x | MIT | Python + torch | PDF, DOCX, PPTX, HTML, images | **Primary** — best layout fidelity, native target for `CanonicalDoc`. v2.118.1 (2026-08-07), 64.4k stars. VLM backend partially closes the gap docling stubs (GLM-OCR/PaddleOCR-VL) were designed to fill — reassess those stubs at §0.4.0. *(verified 2026-08-09)* |
| **Kreuzberg** | Async multi-format extraction facade | MIT (≤4.7); ELv2 (≥4.8, Tier G — see [domain-extraction.md license tier reference](domain-extraction.md#license-tier-reference)) | Python (pypdfium2, Tesseract, python-docx, …) | PDF, Office, images, email, HTML | **Primary (breadth)** — covers the long tail with one adapter. See [ADR-0005](../adr/0005-kreuzberg-elv2-license-boundary.md). **Upstream moved (2026-07/08):** `kreuzberg-dev/kreuzberg` now redirects to **`xberg-io/xberg`** (Rust core, v1.x line, MIT, 8.9k stars, active 2026-08-08), and a separate **`kreuzberg-dev/kreuzberg-lts`** ships MIT releases for the v4 line past the v4.8 ELv2 cut. Both may relax the ADR-0005 pin — see [Open questions](#open-questions) before the next version bump. *(verified 2026-08-09)* |
| **claude_cli_adapter** | LLM-based extraction via Claude Code CLI | n/a (our code) | Claude CLI | Any (LLM-mediated) | **Primary (reference)** — end-to-end wired first; cross-validation baseline. |
| **GLM-OCR** | Vision-LLM OCR for complex scans | Apache-2.0 | GPU preferred | Images, scanned PDF | Stub adapter — specialized scan/handwriting path. |
| **PaddleOCR-VL** | Vision-LLM OCR, CJK-strong; PP-OCRv5 + PP-StructureV3 + PP-ChatOCRv4 in v3.0+ | Apache-2.0 | GPU preferred | Images, scanned PDF | **Optional (CJK PDF primary)** — v3.7.0 (2026-06-11), 87.3k stars. Promoted from stub; PP-OCRv5 is a major VLM upgrade that makes this a direct competitor to docling for CJK PDFs. Gate behind `[paddleocr]` extra; benchmark against docling at §0.4.0. *(verified 2026-08-09)* |
| **olmOCR** ([repo](https://github.com/allenai/olmocr)) | VLM OCR (Qwen2.5-VL 7B) → clean text/Markdown | Apache-2.0 (Tier A) | **GPU** ≥12 GB VRAM; vLLM + poppler; ~30 GB disk | PDF, PNG, JPEG | **Stub adapter** — v0.4.27 (2026-03), 19.3k stars; no commits since 2026-03-25 — treat the maintenance signal as weakening. Apache-2.0 VLM scan path; English-heavy alternative to GLM-OCR. GPU-bound → `[olmocr]` extra; benchmark vs PaddleOCR-VL at §0.4.0. *(verified 2026-08-09)* |
| **DeepSeek-OCR** ([repo](https://github.com/deepseek-ai/DeepSeek-OCR)) | VLM OCR — "contexts optical compression": renders pages as vision tokens to recover text/layout at a fraction of the token cost of raw-text ingestion | MIT (code **and** weights) | Python + torch; GPU preferred | Images, scanned/complex PDF | **Stub adapter** — 23.8k stars; rolling repo with no tagged releases (last push 2026-01-27; base model shipped 2025-10-20). Cleanest licence and largest user base of the VLM-OCR entrants surveyed — a direct MIT competitor to the GLM-OCR / olmOCR stub cohort. Reassess against those stubs at [§0.4.0](../roadmap.md#040--adapters). *(added 2026-08-09)* |
| **Tesseract** | Classical OCR engine | Apache-2.0 | Native C++ binary | Images, scanned PDF | **Transitive** — reached via Kreuzberg/docling; baseline OCR floor, not a direct adapter. |
| **PyMuPDF (fitz)** | Fast PDF text + layout + images | **AGPL-3.0** (or commercial) | Python + native | PDF | **Optional only** — best-in-class for born-digital PDFs, but AGPL would bleed into consumers. Ship behind an opt-in extra. |
| **pdfplumber** ([repo](https://github.com/jsvine/pdfplumber)) | Per-word/char bounding boxes + table extraction (born-digital) | MIT (Tier A) | Pure-Python (pdfminer.six + Pillow); no GPU | PDF (born-digital) | **Optional (geometry/tables)** — v0.11.10 (2026-06-15), 10.6k stars. Pure-Python `LayoutBlock` geometry + tables for born-digital PDFs and a docling cross-check; fills `bbox`/`text` but not semantic `kind` (no classifier). Weak on scans. See [ADR-0011](../adr/0011-content-layout-owned-by-docling.md). *(verified 2026-08-09)* |
| **pdfminer.six** ([repo](https://github.com/pdfminer/pdfminer.six)) | Char-level PDF text + positions | MIT (Tier A) | Pure-Python | PDF | **Transitive** — pdfplumber's engine; reach it through pdfplumber's API, not a direct adapter. |
| **MinerU** (`opendatalab/MinerU`) | Layout-aware PDF/Office → Markdown/JSON; layout-analysis + OCR + table/formula models; strong CJK | **Apache-2.0 + additional terms** (Tier G — see [domain-extraction.md license tier reference](domain-extraction.md#license-tier-reference)): commercial threshold at 100M MAU / USD 20M MRR triggers separate commercial licence; mandatory online-service attribution; auto-termination on non-compliance. GitHub flags as `NOASSERTION`. | Python; GPU strongly preferred (CPU very slow); models ~3-5 GB | PDF, DOCX, PPTX, XLSX | **Opt-in extra (`[mineru]`)** — 77.2 k stars, `mineru-3.4.4-released` (2026-07-10; v4.0.0-alpha series in progress), used by Knowhere as default parser ([e2e-systems.md §2](e2e-systems.md#2-oss-e2e-systems)). Complementary to docling for CJK + complex-layout PDFs. Same Tier-G treatment as Kreuzberg ELv2 ([issue #76](https://github.com/qte77/doc-pipeline-engine/issues/76)): document the thresholds + attribution duty before shipping in any default profile. *(verified 2026-08-09)* |
| **marker** ([repo](https://github.com/datalab-to/marker)) | Layout-aware PDF → Markdown; depends on surya (Apache-2.0 code; RAIL-M weights) for layout detection | **Apache-2.0** (code, since v2.0.0); bundled model weights remain **modified OpenRAIL-M** `MODEL_LICENSE` (Tier G — see [domain-extraction.md license tier reference](domain-extraction.md#license-tier-reference)) | Python + torch; GPU preferred (v2.0.0 adds CPU support) | PDF, DOCX, images | **Optional (weights gate only)** — v2.0.0 (2026-07-20), 38.6k stars. The "Marker 2" rewrite relicensed marker's own code GPL-3.0 → Apache-2.0, so the code-level gate is lifted. Bundled weights still carry a modified OpenRAIL-M `MODEL_LICENSE` (free below USD 5M prior-year revenue *or* USD 5M total equity/debt funding; above either threshold commercial use needs a paid Datalab licence) — same posture as surya. Gate the weight download behind `[marker]`, not the package import. *(licence change verified 2026-08-09)* |
| **Chandra** ([repo](https://github.com/datalab-to/chandra)) | VLM OCR (4B, from the marker/surya team) — complex tables, forms, handwriting, chemistry (SMILES) | Code Apache-2.0; weights **modified OpenRAIL-M** `MODEL_LICENSE` (Tier G — same $5M revenue/funding threshold as marker) | Python + torch; GPU preferred | PDF, images, handwriting, chemistry | **Opt-in (gate)** — Chandra 2.1 (2026-06-17), 12.0k stars, ~monthly cadence. Same org and identical Tier-G weights pattern already gated for marker/surya; gate behind `[chandra]` and keep out of the default install. Reported to top the olmOCR benchmark (~85.9%) — vendor-reported, not independently replicated. *(added 2026-08-09)* |
| **LibreOffice / soffice** ([site](https://www.libreoffice.org/)) | Format-faithful Office conversion engine (legacy `.doc`/`.xls`/`.ppt`, ODF `.odt`/`.ods`/`.odp`, complex `.rtf`); `--cat` dumps text to stdout, `--accept=socket,…;urp` enables persistent UNO daemon | **MPL-2.0 OR LGPL-3.0-or-later** (subprocess-safe; copyleft does not propagate through process boundary) | Native binary; ~200–300 MB RSS; 2–20 s cold start | All Office + ODF + RTF + many more (HTML, EPUB, PDF input/output) | **Candidate (landscape only)** — the 25.8 line reached EOL 2026-06-12; the current Fresh line is 26.2.5 (2026-07-23) — target 26.2.x for any future benchmark. Actively maintained by The Document Foundation. Gap-filler for ODF, complex RTF, legacy `.ppt`/`.xls` where docling and Kreuzberg have lower fidelity. Not wired yet — operational complexity (cold start, profile lock contention) defers to [§0.4.0](../roadmap.md#040--adapters). If gaps confirmed there, ship behind `[libreoffice]` extra. *(verified 2026-08-09)* |
| **anydoc** ([repo](https://github.com/firecrawl/anydoc)) | Rust-native multi-format → GitHub-Flavored-Markdown converter (Firecrawl org); byte-sniffed format detection, deterministic, no ML | MIT (Tier A) | Rust core; native Python wheel via PyO3 (PyPI package is **`firecrawl-anydoc`**, not `anydoc`) — no subprocess, GPU, or JVM; also Node.js and WASM bindings | Word (doc/docx/docm), PowerPoint (ppt/pptx/pptm), Excel (xls/xlsx/xlsb), OpenDocument (odt/ods/odp), RTF, EPUB, CSV, PDF (text layer only — no OCR) | **Candidate (breadth benchmark vs Kreuzberg/LibreOffice at §0.4.0)** — v0.1.7 (2026-08-07), 12.1k stars, but the repo was created 2026-08-03: the star count is launch-marketing reach, not a track record, and criterion 6 is simply not yet answerable. Emits flat Markdown with no `bbox`/`kind`, so it is **not** `content.layout`-eligible ([ADR-0011](../adr/0011-content-layout-owned-by-docling.md)) — it competes with Kreuzberg's breadth role and LibreOffice's ODF/RTF/legacy-Office gap, not with docling. Scanned-PDF OCR is not implemented locally at all; it exists only behind Firecrawl's separate hosted "Parse" API (cloud, API key, ~1,000 free credits/month) — flag `data_locality: cloud` if that path is ever wired. *(added 2026-08-09)* |
| **Unstructured** ([repo](https://github.com/Unstructured-IO/unstructured)) | ETL library partitioning 60+ formats into typed elements (Title, NarrativeText, Table, Image, …) | Apache-2.0 | Python; optional native deps per format | PDF, Office, email, HTML, images (60+ formats) | **Candidate (breadth, benchmark vs Kreuzberg)** — 15.3k stars, active (last push 2026-08-04). Already referenced indirectly elsewhere in the catalog (Transitive chunker in [process.md §1](process.md#1-chunking-strategies), element schema in [process.md §5](process.md#5-normalization-to-canonicaldoc), "Adjacent" in [e2e-systems.md §2](e2e-systems.md#2-oss-e2e-systems)) but had no row here despite being the most natural head-to-head for Kreuzberg's **Primary (breadth)** claim — same licence class, comparable scope. Benchmark at [§0.4.0](../roadmap.md#040--adapters) before any promotion. *(added 2026-08-09)* |
| **MarkItDown** ([repo](https://github.com/microsoft/markitdown)) | Lightweight PDF/Office/image/audio/HTML/ZIP → LLM-ready Markdown converter (Microsoft AutoGen team) | MIT | Python; optional LLM image-captioning, optional Azure Document Intelligence backend | PDF, Office, images, audio, HTML, ZIP | **Not adopted** — v0.1.7 (2026-07-29), 172k stars (~2.7× docling's). Documented explicitly, following the [ADR-0011](../adr/0011-content-layout-owned-by-docling.md) precedent for LiteParse/OmniParse, because the adoption scale makes "why not MarkItDown?" a predictable question. Redundant with Kreuzberg's breadth role, and weaker PDF layout fidelity than docling — no `bbox`/`kind`, so not `content.layout`-eligible. *(added 2026-08-09)* |
| **Apache Tika** | Broad content-extraction server | Apache-2.0 | **JVM** | ~1000+ formats | **Optional (server-mode)** — JVM dep too heavy as default; useful as a remote adapter for enterprise consumers with existing Tika infra. |
| **LiteParse** ([repo](https://github.com/run-llama/liteparse)) | Spatial PDF/Office/image parse with per-line bounding boxes | Apache-2.0 (Tier A) | **Node.js ≥18 CLI** (Rust core; Python pkg subprocesses it); bundled `tesseract-rs` for OCR; ImageMagick for images/SVG | PDF, Office, images, SVG | **Not adopted** — `node-v2.11.1` / `wasm-v2.11.1` (2026-08-05), ~12k stars. Spiked 2026-06-11: clean per-line bboxes (976 items from a 15-pp PDF in ~10.5 s), but its layout edge is already covered Python-natively by docling + pdfplumber without the Node runtime + native-dep tax (bundled `tesseract-rs` ignores system Tesseract; SVG needs system ImageMagick). See [ADR-0011](../adr/0011-content-layout-owned-by-docling.md). *(verified 2026-08-09)* |
| **OmniParse** ([repo](https://github.com/adithya-s-k/omniparse)) | GenAI-oriented multi-modal parse server (Surya/Florence-2/Whisper/Marker/Crawl4AI) | **GPL-3.0** code (Tier F) + **cc-by-nc-sa-4.0** weights (Tier E, NonCommercial) | **GPU** 8–10 GB VRAM; Docker/REST server | PDF, Office, images, audio, video, web | **Avoid** — 7.6k stars. NonCommercial weights (Tier E) + GPL-3.0 (Tier F) + GPU server fail the licence and footprint criteria; audio/video/web breadth is out of scope. Not an adapter or an extra. |
| **TurboOCR** ([repo](https://github.com/aiptimizer/TurboOCR)) | GPU/TensorRT C++ microservice recompiling PaddleOCR's PP-OCRv6 (OCR) + PP-DocLayoutV3 (layout) + PP-FormulaNet-S (formula) + SLANet-Plus (tables) for throughput | MIT code (Tier A) over Apache-2.0 PaddleOCR weights — licence is clean and is **not** the rejection reason | **Docker/GPU microservice** (Linux, NVIDIA Turing+, 4–8 GB VRAM); HTTP/gRPC only — the PyPI `turboocr` package is a remote client, not an in-process engine; CPU image exists but forfeits the speed premise | Images, PDF (EN/ZH/JA) | **Not adopted** — v3.5.0 (2026-07-20), 933 stars, repo created 2026-03-20. Adds no format or language coverage beyond the catalogued PaddleOCR-VL row — it reimplements the same PP-OCR weight family, trading the VLM component for raw speed. An independent review corroborates the throughput (~28 pages/s on an RTX 4090) but measures ~90% character accuracy against PaddleOCR-VL's ~96%, and TEDS 0.000 for table structure in the tested configuration. Note the Docker-service shape alone is *not* disqualifying here (cf. GROBID, Tika) — the redundancy is. *(added 2026-08-09)* |
| **dots.ocr** ([repo](https://github.com/studio-dots-ai/dots.ocr)) | Compact 1.7B multilingual VLM unifying layout detection + OCR in a single model | **Licence conflict (Tier G, unresolved)** — the repo ships *two* licence files: a 1 KB `LICENSE` (MIT) **and** a 15 KB `dots.ocr LICENSE AGREEMENT`; `requirements.txt` additionally hard-pulls **PyMuPDF (AGPL-3.0)** as a non-optional dependency | Python + torch; GPU preferred | Images, scanned PDF, multilingual | **Avoid** — 9.1k stars, no tagged releases (last push 2026-03-24). Two contradictory licence files plus an undisclosed AGPL-3.0 hard dependency is exactly the trap [ADR-0005](../adr/0005-kreuzberg-elv2-license-boundary.md) exists to catch: the MIT badge cannot be relied on, and the AGPL transitive would bleed into embedding consumers. Do not adopt until upstream resolves the conflict and makes the PyMuPDF dependency optional. *(added 2026-08-09)* |

### Notes

**docling vs Kreuzberg** — not redundant. docling is the layout-accurate path for PDFs that feed `CanonicalDoc`; Kreuzberg is the pragmatic catch-all for the formats docling doesn't handle well (email, xlsx, legacy Office). Run them side by side in [§0.4.0](../roadmap.md#040--adapters) cross-validation.

**Tesseract positioning** — don't expose as its own adapter. It's a dependency of the Python wrappers; surfacing it separately would duplicate configuration surface for no gain.

**PyMuPDF license risk** — AGPL triggers on *distribution* of derived works. Because consumers (polyforge, office-polyforge) embed us, an AGPL hard dep would force them to AGPL as well. Keep it behind `pip install doc-pipeline-engine[pymupdf]` so the choice is explicit and downstream.

**MinerU license risk** — GitHub reports `NOASSERTION`. Reading the LICENSE file directly: Apache-2.0 *plus* a Llama-style commercial threshold (100M MAU OR USD 20M MRR), a mandatory online-service attribution clause, and auto-termination on non-compliance. Same Tier-G treatment as Kreuzberg ELv2. Practical impact: fine for internal and SMB use, but cannot redistribute as plain Apache-2.0 without surfacing the restrictions; cannot run as an unbranded online service. Gate behind `pip install doc-pipeline-engine[mineru]` and document the thresholds + attribution duty in the NOTICE file before any default-profile inclusion.

**Tika cost/benefit** — once you need a JVM, operations teams notice. Ship as a remote-server adapter (`tika.url=...`) rather than an embedded dep, so Java stays out of our install footprint.

**LibreOffice / soffice adoption path** — actively maintained (v25.8.7.2, 2026-05) and licence-clean (MPL-2.0 OR LGPL-3.0-or-later; copyleft does not propagate via subprocess invocation under the standard FSF interpretation — relevant FSF clarification at <https://www.gnu.org/licenses/gpl-faq.html#MereAggregation>). Two-phase adoption when ODF/RTF/legacy-PPT gaps justify it:

- **Phase 1 (subprocess-per-file)** — `soffice --headless --cat <file>` dumps text to stdout. Cleaner than `--convert-to txt` (no intermediate file, no `--outdir`). Per-process isolation via `-env:UserInstallation=file:///tmp/lo-<uuid>` prevents user-profile lock contention under concurrent invocations. Cold-start tax (2–20 s) is the cost.
- **Phase 2 (UNO socket daemon)** — `soffice --headless --accept="socket,host=127.0.0.1,port=2002;urp"` once; subsequent conversions go over UNO (`urp` binary protocol) at near-zero startup. **Sandbox required**: LibreOffice's own help text states *"API access allows execution of arbitrary commands"* — treat the UNO endpoint as a security-sensitive surface. Phase 2 is an architecture decision worth an ADR.
- **Bonus** — `soffice --script-cat <file>` dumps embedded VBA/JS macros without running them. Distinct from text extraction; relevant for any future security/policy gate that needs to detect macro-bearing documents.

Gate decision deferred to [§0.4.0](../roadmap.md#040--adapters): benchmark Kreuzberg vs. LibreOffice on a real ODF / RTF / legacy `.ppt` sample set; if Kreuzberg fidelity is sufficient, **LibreOffice stays a landscape-only entry**.

**Bounding boxes / `content.layout` ownership** — `ExtractionBundle.content.layout` (a `LayoutBlock` list: `kind`, `page`, `bbox`, `level`, `text`) is the provenance anchor that `CanonicalDoc.Node.source_refs` indexes into; an empty layout severs canonical-node → source traceability. docling is the only surveyed backend that emits geometry **and** semantic `kind` **and** provenance, so it owns layout population; pdfplumber is a pure-Python born-digital cross-check (geometry only — no `kind`). External bbox parsers evaluated and **not** adopted: **LiteParse** (Apache-2.0 but a Node ≥18 subprocess; bbox redundant with docling/pdfplumber) and **OmniParse** (GPL-3.0 + NonCommercial weights + GPU). Full rationale: [ADR-0011](../adr/0011-content-layout-owned-by-docling.md).

## 2. Source connectors

Wired behind a `SourceConnector` interface. Emit file lists / blob handles consumed by extraction.

| Tool | Source system | License | Runtime | Auth | Locality | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **msgraph-sdk** | SharePoint / OneDrive (MS Graph) | MIT | Python-native | OAuth 2.0 (MSAL / client-credentials) | cloud | **Primary** — official Microsoft SDK; covers SharePoint and OneDrive via single Graph surface. |
| **O365** | SharePoint / OneDrive (MS Graph) | Apache-2.0 | Python-native | OAuth 2.0 / device flow | cloud | **Optional (maintenance concern)** — only 2 releases ever (v2.0 in 2019, v2.1 in 2025-02); commits paused 2026-03-10. Prefer `msgraph-sdk`; use O365 only where its device-flow surface is a hard requirement. |
| **atlassian-python-api** | Confluence (REST v1/v2) | Apache-2.0 | Python-native | API token / OAuth 2.0 | cloud or on-prem | **Primary** — canonical community SDK; covers Cloud and Server; exposes page-tree traversal. |
| **google-api-python-client** | Google Drive | Apache-2.0 | Python-native | OAuth 2.0 / service account | cloud | **Primary** — official Google client; stable. |
| **boto3** | S3 / object storage (AWS, MinIO via `endpoint_url`) | Apache-2.0 | Python-native | IAM / STS / assume-role | cloud or local | **Primary** — de-facto standard; covers S3-compatible stores. |
| **imapclient** | IMAP / email | BSD-3-Clause | Python-native | Password / XOAUTH2 | cloud or on-prem | **Primary** — thin Pythonic IMAP4 wrapper; pairs with `email` stdlib. |
| **exchangelib** | Exchange / Outlook (EWS) | BSD-2-Clause | Python-native | NTLM / OAuth 2.0 / Basic | on-prem or cloud | **Optional** — covers EWS where Graph is unavailable (older / hybrid Exchange). |

### Connector notes

**msgraph-sdk vs O365** — prefer `msgraph-sdk` as primary; it is the officially maintained Microsoft library and maps 1:1 to Graph API docs. O365 stays as an optional shim.

**Data-locality flagging** — every cloud-source connector must declare `data_locality: cloud` so the [§0.5.0](../roadmap.md#050--domain-packs) policy layer can refuse to load it under a `local-only` profile. On-prem variants (EWS, Confluence Server, S3-compatible MinIO) are local-friendly.

**boto3 endpoint override** — pass `endpoint_url` to reach MinIO, Backblaze B2, or other S3-compatible stores. No fork required.

**Email split** — `imapclient` covers most cloud and on-prem mail; `exchangelib` covers the EWS-only subset. Register both behind a common `EmailConnector`.

## 3. Crawling / discovery

Produce the file list that becomes `DiscoveryManifest` (`version`, `source`, `discovered_at`, `files`).

| Tool | Role | License | Runtime | `DiscoveryManifest` fit | Verdict |
| --- | --- | --- | --- | --- | --- |
| **polyfetch-scrape** (sibling repo) | Web crawl → URL/file list | Apache-2.0 (internal) | Python-native | Native — already emits structured manifests | **Primary (web)** — purpose-built sibling; reuse output as `DiscoveryManifest` directly. |
| **trafilatura** | Web content extraction + URL crawl | Apache-2.0 | Python-native | Adapt URL list to `files[]` | **Optional (targeted web)** — v2.2.0 (2026-07-31), 6.5k stars. Breaking change introduced in v2.0.0: `bare_extraction()` returns a `Document` object, not `dict`; `no_fallback` renamed to `fast`. Update any callers before upgrading from v1.x. *(verified 2026-08-09)* |
| **httpx** | HTTP client for bespoke crawlers | BSD-3-Clause | Python-native | Raw — caller builds manifest | **Building block** — async-native, HTTP/2; recommended base for custom connector fetch loops. |
| **pathlib** (stdlib) | Local file-tree walk | PSF (stdlib) | Python-native | Direct — `Path.rglob()` → `files[]` | **Primary (local)** — zero dep; the canonical filesystem path. |
| **watchdog** | Filesystem event watcher | Apache-2.0 | Python-native (optional C ext) | Incremental — emits change events for manifest deltas | **Optional** — v6.0.0 (2024-11-01, still the latest release) removed deprecated `echo` utilities; inotify backend now uses `select.poll()`. API-compatible for standard usage but review any `echo`-based code before upgrading from v5. *(verified 2026-08-09)* |
| **scrapy** | Full crawl engine | BSD-3-Clause | Python-native | Adapter needed — Spider yields URLs | **Optional** — justified only for large multi-domain crawls. |
| **crawl4ai** ([repo](https://github.com/unclecode/crawl4ai)) | LLM-targeted async web crawl with JS rendering | Apache-2.0 | Python-native (Playwright for JS) | URL list to `files[]` via structured extraction | **Optional (JS-heavy sites)** — v0.9.2 (2026-07-15), 77.4k stars. Complement to trafilatura for SPA/JS-rendered pages where trafilatura's static-HTML path fails. Gate behind `[crawl4ai]` extra (Playwright dep). *(verified 2026-08-09)* |
| **ColPali** ([repo](https://github.com/illuin-tech/colpali)) | VLM page-image retrieval model | MIT | Python + torch; GPU preferred | PDF page images | **Candidate (relevance filter)** — v0.3.17 (2026-06-08), 2.7k stars. Not an extractor; sits upstream as a relevance-filter layer ahead of extraction for large corpora. Relevant for §0.5.0 domain packs. *(verified 2026-08-09)* |

### Discovery notes

**polyfetch-scrape as the seam** — sibling repo under the same governance; keep its output schema in lockstep with `DiscoveryManifest`. It is the canonical web-crawl provider.

**pathlib vs watchdog** — `pathlib.rglob()` covers batch/cold-start; `watchdog` covers incremental/warm. Both must produce the same `DiscoveryManifest` shape so downstream stages stay uniform.

**trafilatura vs scrapy** — trafilatura wins on footprint for single-site targeted crawls; scrapy wins for multi-domain breadth-first crawls with retry/politeness requirements.

## See also

- [ai-agents-research / CC-web-scraping-plugins-analysis.md](https://github.com/qte77/ai-agents-research/blob/main/docs/cc-native/plugins-ecosystem/CC-web-scraping-plugins-analysis.md) — Claude Code plugins for web scraping, at the orchestration layer above the connectors and crawlers surveyed here.
- [../prototype/plan.md](../prototype/plan.md) — how the candidates surveyed here get exercised in the v1 dual-variant prototype.

## Open questions

- Should `DiscoveryManifest.source` be an enum (cloud-source ID) or a free string?
- MS Graph throttling (429 / `Retry-After`) — does the connector layer own retry, or does polyfetch-scrape's fetch layer absorb it?
- Adapter registry policy across extractors: first-match, ensemble, or declared per-domain? → revisit during [§0.5.0 — Domain packs](../roadmap.md#050--domain-packs).
- Minimum cross-validation set: which adapters must agree on which sample categories to call extraction "verified"?
- Do we need handwriting OCR in scope for [§0.4.0](../roadmap.md#040--adapters), or defer with GLM-OCR? → see AGENT_REQUESTS.md if raised.
- watchdog watch-mode: in-scope for the [§0.5.0](../roadmap.md#050--domain-packs) streaming milestone, or defer to a separate `ingest-streaming` extra?
- Kreuzberg upstream moved: `kreuzberg-dev/kreuzberg` now redirects to `xberg-io/xberg` (MIT, Rust-core v1.x), and `kreuzberg-dev/kreuzberg-lts` ships MIT v4 releases past the v4.8 ELv2 cut. Does either path retire the [ADR-0005](../adr/0005-kreuzberg-elv2-license-boundary.md) `<4.8` pin? → run a follow-up research pass on both before the next Kreuzberg version bump; no immediate ADR change.
- marker's code-level gate is lifted (Apache-2.0 since v2.0.0) but its weights stay Tier-G OpenRAIL-M. Should `[marker]` become a default-install extra with a weights-download gate, or stay fully opt-in? → recommended default: stay opt-in, no default-install change.
- Does the anydoc / Unstructured / MarkItDown cohort warrant one shared breadth benchmark against Kreuzberg at [§0.4.0](../roadmap.md#040--adapters), rather than three separate spikes?

## References

### Extraction backends

- docling: <https://github.com/docling-project/docling>
- Kreuzberg: <https://github.com/kreuzberg-dev/kreuzberg>
- xberg (Kreuzberg successor): <https://github.com/xberg-io/xberg>
- Kreuzberg v4 LTS: <https://github.com/kreuzberg-dev/kreuzberg-lts>
- GLM-OCR: <https://github.com/zai-org/GLM-OCR>
- PaddleOCR-VL: <https://github.com/PaddlePaddle/PaddleOCR>
- Tesseract: <https://github.com/tesseract-ocr/tesseract>
- PyMuPDF: <https://github.com/pymupdf/PyMuPDF>
- MinerU: <https://github.com/opendatalab/MinerU>
- olmOCR: <https://github.com/allenai/olmocr>
- pdfplumber: <https://github.com/jsvine/pdfplumber>
- pdfminer.six: <https://github.com/pdfminer/pdfminer.six>
- LiteParse: <https://github.com/run-llama/liteparse>
- OmniParse: <https://github.com/adithya-s-k/omniparse>
- anydoc: <https://github.com/firecrawl/anydoc>
- Unstructured: <https://github.com/Unstructured-IO/unstructured>
- MarkItDown: <https://github.com/microsoft/markitdown>
- DeepSeek-OCR: <https://github.com/deepseek-ai/DeepSeek-OCR>
- Chandra: <https://github.com/datalab-to/chandra>
- TurboOCR: <https://github.com/aiptimizer/TurboOCR>
- dots.ocr: <https://github.com/studio-dots-ai/dots.ocr>
- LibreOffice: <https://www.libreoffice.org/>
- LibreOffice licences: <https://www.libreoffice.org/about-us/licenses/>
- Apache Tika: <https://tika.apache.org/>

### Source connectors

- msgraph-sdk: <https://github.com/microsoftgraph/msgraph-sdk-python>
- O365: <https://github.com/O365/python-o365>
- atlassian-python-api: <https://github.com/atlassian-api/atlassian-python-api>
- google-api-python-client: <https://github.com/googleapis/google-api-python-client>
- boto3: <https://github.com/boto/boto3>
- imapclient: <https://github.com/mjs/imapclient>
- exchangelib: <https://github.com/ecederstrand/exchangelib>

### Crawling / discovery

- trafilatura: <https://github.com/adbar/trafilatura>
- httpx: <https://github.com/encode/httpx>
- scrapy: <https://github.com/scrapy/scrapy>
- watchdog: <https://github.com/gorakhargosh/watchdog>
- crawl4ai: <https://github.com/unclecode/crawl4ai>
- ColPali: <https://github.com/illuin-tech/colpali>
- marker: <https://github.com/datalab-to/marker>
- surya: <https://github.com/datalab-to/surya>
