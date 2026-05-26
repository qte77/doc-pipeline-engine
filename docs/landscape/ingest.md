---
title: Ingest Landscape
purpose: Survey of extraction backends, source connectors, and crawling/discovery providers for the ingest stage
created: 2026-04-26
updated: 2026-05-26
validated_links: 2026-05-26
category: landscape
---

Survey of candidates for the **ingest** stage — extraction backends, source connectors, and crawling/discovery providers. Companion files: [process.md](process.md), [output.md](output.md), [e2e-systems.md](e2e-systems.md), [domain-extraction.md](domain-extraction.md).

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
| **docling** | Layout-aware PDF/Office → structured doc; native VLM pipeline (Granite Vision 4.1) added v2.x | MIT | Python + torch | PDF, DOCX, PPTX, HTML, images | **Primary** — best layout fidelity, native target for `CanonicalDoc`. v2.95.0 (2026-05-21), 60k stars. VLM backend partially closes the gap docling stubs (GLM-OCR/PaddleOCR-VL) were designed to fill — reassess those stubs at §0.4.0. |
| **Kreuzberg** | Async multi-format extraction facade | MIT (≤4.7); ELv2 (≥4.8, Tier G — see [domain-extraction.md license tier reference](domain-extraction.md#license-tier-reference)) | Python (pypdfium2, Tesseract, python-docx, …) | PDF, Office, images, email, HTML | **Primary (breadth)** — covers the long tail with one adapter. See [ADR-0005](../adr/0005-kreuzberg-elv2-license-boundary.md). |
| **claude_cli_adapter** | LLM-based extraction via Claude Code CLI | n/a (our code) | Claude CLI | Any (LLM-mediated) | **Primary (reference)** — end-to-end wired first; cross-validation baseline. |
| **GLM-OCR** | Vision-LLM OCR for complex scans | Apache-2.0 | GPU preferred | Images, scanned PDF | Stub adapter — specialized scan/handwriting path. |
| **PaddleOCR-VL** | Vision-LLM OCR, CJK-strong; PP-OCRv5 + PP-StructureV3 + PP-ChatOCRv4 in v3.0+ | Apache-2.0 | GPU preferred | Images, scanned PDF | **Optional (CJK PDF primary)** — v3.5.0 (2026-05-19), 79k stars. Promoted from stub; PP-OCRv5 is a major VLM upgrade that makes this a direct competitor to docling for CJK PDFs. Gate behind `[paddleocr]` extra; benchmark against docling at §0.4.0. |
| **Tesseract** | Classical OCR engine | Apache-2.0 | Native C++ binary | Images, scanned PDF | **Transitive** — reached via Kreuzberg/docling; baseline OCR floor, not a direct adapter. |
| **PyMuPDF (fitz)** | Fast PDF text + layout + images | **AGPL-3.0** (or commercial) | Python + native | PDF | **Optional only** — best-in-class for born-digital PDFs, but AGPL would bleed into consumers. Ship behind an opt-in extra. |
| **MinerU** (`opendatalab/MinerU`) | Layout-aware PDF/Office → Markdown/JSON; layout-analysis + OCR + table/formula models; strong CJK | **Apache-2.0 + additional terms** (Tier G — see [domain-extraction.md license tier reference](domain-extraction.md#license-tier-reference)): commercial threshold at 100M MAU / USD 20M MRR triggers separate commercial licence; mandatory online-service attribution; auto-termination on non-compliance. GitHub flags as `NOASSERTION`. | Python; GPU strongly preferred (CPU very slow); models ~3-5 GB | PDF, DOCX, PPTX, XLSX | **Opt-in extra (`[mineru]`)** — 64.8 k stars, v3.1.15 (2026-05-19), used by Knowhere as default parser ([e2e-systems.md §2](e2e-systems.md#2-oss-e2e-systems)). Complementary to docling for CJK + complex-layout PDFs. Same Tier-G treatment as Kreuzberg ELv2 ([issue #76](https://github.com/qte77/doc-pipeline-engine/issues/76)): document the thresholds + attribution duty before shipping in any default profile. |
| **marker** ([repo](https://github.com/datalab-to/marker)) | Layout-aware PDF → Markdown; depends on surya (GPL-3.0) for layout detection | **GPL-3.0** (Tier G — see [domain-extraction.md license tier reference](domain-extraction.md#license-tier-reference)) | Python + torch; GPU preferred | PDF, DOCX, images | **Opt-in (gate)** — v1.10.2 (2026-05), 35k stars. Strong on complex PDFs; GPL-3.0 chains from surya hard dep. Same gate pattern as PyMuPDF: `pip install doc-pipeline-engine[marker]` only; must not appear in default install. |
| **LibreOffice / soffice** ([site](https://www.libreoffice.org/)) | Format-faithful Office conversion engine (legacy `.doc`/`.xls`/`.ppt`, ODF `.odt`/`.ods`/`.odp`, complex `.rtf`); `--cat` dumps text to stdout, `--accept=socket,…;urp` enables persistent UNO daemon | **MPL-2.0 OR LGPL-3.0-or-later** (subprocess-safe; copyleft does not propagate through process boundary) | Native binary; ~200–300 MB RSS; 2–20 s cold start | All Office + ODF + RTF + many more (HTML, EPUB, PDF input/output) | **Candidate (landscape only)** — v25.8.7.2 (2026-05); actively maintained by The Document Foundation. Gap-filler for ODF, complex RTF, legacy `.ppt`/`.xls` where docling and Kreuzberg have lower fidelity. Not wired yet — operational complexity (cold start, profile lock contention) defers to [§0.4.0](../roadmap.md#040--adapters). If gaps confirmed there, ship behind `[libreoffice]` extra. |
| **Apache Tika** | Broad content-extraction server | Apache-2.0 | **JVM** | ~1000+ formats | **Optional (server-mode)** — JVM dep too heavy as default; useful as a remote adapter for enterprise consumers with existing Tika infra. |

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
| **trafilatura** | Web content extraction + URL crawl | Apache-2.0 | Python-native | Adapt URL list to `files[]` | **Optional (targeted web)** — v2.0.0 (2025-09); breaking change: `bare_extraction()` now returns a `Document` object, not `dict`; `no_fallback` renamed to `fast`. Update any callers before upgrading. 6k stars. |
| **httpx** | HTTP client for bespoke crawlers | BSD-3-Clause | Python-native | Raw — caller builds manifest | **Building block** — async-native, HTTP/2; recommended base for custom connector fetch loops. |
| **pathlib** (stdlib) | Local file-tree walk | PSF (stdlib) | Python-native | Direct — `Path.rglob()` → `files[]` | **Primary (local)** — zero dep; the canonical filesystem path. |
| **watchdog** | Filesystem event watcher | Apache-2.0 | Python-native (optional C ext) | Incremental — emits change events for manifest deltas | **Optional** — v6.0.0 (2026-05-07) removed deprecated `echo` utilities; inotify backend now uses `select.poll()`. API-compatible for standard usage but review any `echo`-based code before upgrading from v5. |
| **scrapy** | Full crawl engine | BSD-3-Clause | Python-native | Adapter needed — Spider yields URLs | **Optional** — justified only for large multi-domain crawls. |
| **crawl4ai** ([repo](https://github.com/unclecode/crawl4ai)) | LLM-targeted async web crawl with JS rendering | Apache-2.0 | Python-native (Playwright for JS) | URL list to `files[]` via structured extraction | **Optional (JS-heavy sites)** — v0.8.5 (2026-05-25), 66k stars. Complement to trafilatura for SPA/JS-rendered pages where trafilatura's static-HTML path fails. Gate behind `[crawl4ai]` extra (Playwright dep). |
| **ColPali** ([repo](https://github.com/illuin-tech/colpali)) | VLM page-image retrieval model | MIT | Python + torch; GPU preferred | PDF page images | **Candidate (relevance filter)** — v0.3.16 (2026-05-19), 3k stars. Not an extractor; sits upstream as a relevance-filter layer ahead of extraction for large corpora. Relevant for §0.5.0 domain packs. |

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

## References

### Extraction backends

- docling: <https://github.com/docling-project/docling>
- Kreuzberg: <https://github.com/kreuzberg-dev/kreuzberg>
- GLM-OCR: <https://github.com/zai-org/GLM-OCR>
- PaddleOCR-VL: <https://github.com/PaddlePaddle/PaddleOCR>
- Tesseract: <https://github.com/tesseract-ocr/tesseract>
- PyMuPDF: <https://github.com/pymupdf/PyMuPDF>
- MinerU: <https://github.com/opendatalab/MinerU>
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
