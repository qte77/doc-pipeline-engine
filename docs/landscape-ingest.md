# Ingest Landscape

Survey of candidates for the **ingest** stage — extraction backends, source connectors, and crawling/discovery providers. Companion files: [landscape-process.md](landscape-process.md), [landscape-output.md](landscape-output.md), [landscape-prior-art.md](landscape-prior-art.md).

## Selection criteria

1. **License compatibility** — must not force Apache-2.0 consumers into copyleft obligations. AGPL/GPL tools are optional-only.
2. **Format coverage / source coverage** — what the tool actually reaches.
3. **Runtime footprint** — Python-native preferred; JVM/heavy native deps must justify themselves.
4. **Auth/credential model** — for source connectors, must support OAuth 2.0 / service-account flows.
5. **Data-locality fit** — note cloud-only paths; relevant to §0.5 `local-only` / `claude-api-extracted-only` / `cloud-redacted` policies.
6. **Maintenance signal** — active releases, non-trivial user base.

## 1. Extraction backends

Wired as adapters behind `base/adapter.py`. Emit `ExtractionBundle`.

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

### Notes

**docling vs Kreuzberg** — not redundant. docling is the layout-accurate path for PDFs that feed `CanonicalDoc`; Kreuzberg is the pragmatic catch-all for the formats docling doesn't handle well (email, xlsx, legacy Office). Run them side by side in 0.4.0 cross-validation.

**Tesseract positioning** — don't expose as its own adapter. It's a dependency of the Python wrappers; surfacing it separately would duplicate configuration surface for no gain.

**PyMuPDF license risk** — AGPL triggers on *distribution* of derived works. Because consumers (polyforge, office-polyforge) embed us, an AGPL hard dep would force them to AGPL as well. Keep it behind `pip install doc-pipeline-engine[pymupdf]` so the choice is explicit and downstream.

**Tika cost/benefit** — once you need a JVM, operations teams notice. Ship as a remote-server adapter (`tika.url=...`) rather than an embedded dep, so Java stays out of our install footprint.

## 2. Source connectors

Wired behind a `SourceConnector` interface. Emit file lists / blob handles consumed by extraction.

| Tool | Source system | License | Runtime | Auth | Locality | Verdict |
|---|---|---|---|---|---|---|
| **msgraph-sdk** | SharePoint / OneDrive (MS Graph) | MIT | Python-native | OAuth 2.0 (MSAL / client-credentials) | cloud | **Primary** — official Microsoft SDK; covers SharePoint and OneDrive via single Graph surface. |
| **O365** | SharePoint / OneDrive (MS Graph) | Apache-2.0 | Python-native | OAuth 2.0 / device flow | cloud | **Optional** — friendlier surface than msgraph-sdk; less actively maintained. |
| **atlassian-python-api** | Confluence (REST v1/v2) | Apache-2.0 | Python-native | API token / OAuth 2.0 | cloud or on-prem | **Primary** — canonical community SDK; covers Cloud and Server; exposes page-tree traversal. |
| **google-api-python-client** | Google Drive | Apache-2.0 | Python-native | OAuth 2.0 / service account | cloud | **Primary** — official Google client; stable. |
| **boto3** | S3 / object storage (AWS, MinIO via `endpoint_url`) | Apache-2.0 | Python-native | IAM / STS / assume-role | cloud or local | **Primary** — de-facto standard; covers S3-compatible stores. |
| **imapclient** | IMAP / email | BSD-3-Clause | Python-native | Password / XOAUTH2 | cloud or on-prem | **Primary** — thin Pythonic IMAP4 wrapper; pairs with `email` stdlib. |
| **exchangelib** | Exchange / Outlook (EWS) | BSD-2-Clause | Python-native | NTLM / OAuth 2.0 / Basic | on-prem or cloud | **Optional** — covers EWS where Graph is unavailable (older / hybrid Exchange). |

### Connector notes

**msgraph-sdk vs O365** — prefer `msgraph-sdk` as primary; it is the officially maintained Microsoft library and maps 1:1 to Graph API docs. O365 stays as an optional shim.

**Data-locality flagging** — every cloud-source connector must declare `data_locality: cloud` so the §0.5 policy layer can refuse to load it under a `local-only` profile. On-prem variants (EWS, Confluence Server, S3-compatible MinIO) are local-friendly.

**boto3 endpoint override** — pass `endpoint_url` to reach MinIO, Backblaze B2, or other S3-compatible stores. No fork required.

**Email split** — `imapclient` covers most cloud and on-prem mail; `exchangelib` covers the EWS-only subset. Register both behind a common `EmailConnector`.

## 3. Crawling / discovery

Produce the file list that becomes `DiscoveryManifest` (`version`, `source`, `discovered_at`, `files`).

| Tool | Role | License | Runtime | `DiscoveryManifest` fit | Verdict |
|---|---|---|---|---|---|
| **polyfetch-scrape** (sibling repo) | Web crawl → URL/file list | Apache-2.0 (internal) | Python-native | Native — already emits structured manifests | **Primary (web)** — purpose-built sibling; reuse output as `DiscoveryManifest` directly. |
| **trafilatura** | Web content extraction + URL crawl | Apache-2.0 | Python-native | Adapt URL list to `files[]` | **Optional (targeted web)** — lightweight; excellent boilerplate stripping; for single-site crawls where Scrapy overhead is unjustified. |
| **httpx** | HTTP client for bespoke crawlers | BSD-3-Clause | Python-native | Raw — caller builds manifest | **Building block** — async-native, HTTP/2; recommended base for custom connector fetch loops. |
| **pathlib** (stdlib) | Local file-tree walk | PSF (stdlib) | Python-native | Direct — `Path.rglob()` → `files[]` | **Primary (local)** — zero dep; the canonical filesystem path. |
| **watchdog** | Filesystem event watcher | Apache-2.0 | Python-native (optional C ext) | Incremental — emits change events for manifest deltas | **Optional** — for streaming/watch mode; not needed for one-shot batch ingest. |
| **scrapy** | Full crawl engine | BSD-3-Clause | Python-native | Adapter needed — Spider yields URLs | **Optional** — justified only for large multi-domain crawls. |

### Discovery notes

**polyfetch-scrape as the seam** — sibling repo under the same governance; keep its output schema in lockstep with `DiscoveryManifest`. It is the canonical web-crawl provider.

**pathlib vs watchdog** — `pathlib.rglob()` covers batch/cold-start; `watchdog` covers incremental/warm. Both must produce the same `DiscoveryManifest` shape so downstream stages stay uniform.

**trafilatura vs scrapy** — trafilatura wins on footprint for single-site targeted crawls; scrapy wins for multi-domain breadth-first crawls with retry/politeness requirements.

## See also

- [ai-agents-research / CC-web-scraping-plugins-analysis.md](https://github.com/qte77/ai-agents-research/blob/main/docs/cc-native/plugins-ecosystem/CC-web-scraping-plugins-analysis.md) — Claude Code plugins for web scraping, at the orchestration layer above the connectors and crawlers surveyed here.

## Open questions

- Should `DiscoveryManifest.source` be an enum (cloud-source ID) or a free string?
- MS Graph throttling (429 / `Retry-After`) — does the connector layer own retry, or does polyfetch-scrape's fetch layer absorb it?
- Adapter registry policy across extractors: first-match, ensemble, or declared per-domain? → revisit during 0.5.0 domain packs.
- Minimum cross-validation set: which adapters must agree on which sample categories to call extraction "verified"?
- Do we need handwriting OCR in scope for 0.4.0, or defer with GLM-OCR? → see AGENT_REQUESTS.md if raised.
- watchdog watch-mode: in-scope for 0.5.0 streaming milestone, or defer to a separate `ingest-streaming` extra?

## References

### Extraction backends

- docling: <https://github.com/docling-project/docling>
- Kreuzberg: <https://github.com/kreuzberg-dev/kreuzberg>
- GLM-OCR: <https://github.com/THUDM/GLM-4>
- PaddleOCR-VL: <https://github.com/PaddlePaddle/PaddleOCR>
- Tesseract: <https://github.com/tesseract-ocr/tesseract>
- PyMuPDF: <https://github.com/pymupdf/PyMuPDF>
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
