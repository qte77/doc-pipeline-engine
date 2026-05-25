---
title: Process Landscape
purpose: Survey of chunking, table/figure extraction, NER, RAG indexing, schema-templated extraction, and CanonicalDoc normalization for the process stage
created: 2026-04-26
updated: 2026-05-25
validated_links: 2026-05-25
category: landscape
---

Survey of candidates for the **process** stage — chunking, supplemental table/figure extraction, NER, RAG indexing, and normalization to `CanonicalDoc` (`ExtractionBundle → CanonicalDoc`, [roadmap §0.5.0](../roadmap.md#050--domain-packs)). Companion files: [ingest.md](ingest.md), [output.md](output.md), [e2e-systems.md](e2e-systems.md), [domain-extraction.md](domain-extraction.md).

`CanonicalDoc` fields: `version`, `source_sha256`, `built_at`, `input_format`, `root` (normalized tree), `tier_summary` (Quick vs Comprehensive — see [architecture.md](../architecture.md)). "Canonical" means a normalized tree rooted at `root` carrying tier-aware summary.

## Selection criteria

1. **License compatibility** — Apache-2.0 / MIT preferred; AGPL/GPL opt-in only.
2. **Runtime footprint** — Python-native preferred; model downloads and GPU requirements declared.
3. **Data-locality fit** — local-only vs cloud-required; critical for [§0.5.0](../roadmap.md#050--domain-packs) policy enforcement.
4. **Format coverage / domain fit** — chunkers, NER models.
5. **Maintenance signal** — active releases, non-trivial user base.

## 1. Chunking strategies

| Tool | Strategy | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **langchain-text-splitters** | Fixed-size, recursive, Markdown/HTML-aware | MIT | Python, CPU | local | **Primary** — zero-model splits; `MarkdownHeaderTextSplitter` maps onto `CanonicalDoc.root` heading tree. Slim sub-package avoids full LangChain footprint. |
| **llama-index-core** node parsers | Semantic, layout-aware, sentence-window, hierarchical | MIT | Python; some pull sentence-transformers (GPU optional) | local | **Candidate** — `HierarchicalNodeParser` mirrors tier hierarchy; evaluate footprint. |
| **semantic-chunker** | Embedding-similarity boundary detection | MIT | Python + sentence-transformers (~300 MB) | local | **Optional (Comprehensive)** — improves coherence; gate behind `[semantic]` extra. |
| **unstructured** chunking | Layout/title-aware, element-boundary | Apache-2.0 | Python; optional native deps | local | **Transitive** — only when unstructured produced the elements. |
| **adaptive-chunking** (`ekimetrics/adaptive-chunking`) | Per-document method selection via 5 intrinsic quality metrics (size compliance, intrachunk cohesion, contextual coherence, block integrity, missing-reference error); ships 4 default splitters (recursive ×2, page, LLM-regex); pluggable | MIT (core); `[coref]` extra is CC-BY-NC-SA-4.0, `[parsing]` extra is AGPL-3.0 | Python + spaCy; Docling default parser; optional Jina embeddings | local (core) | **Candidate (Comprehensive)** — LREC 2026 paper (arXiv 2603.25333); 67.7 retrieval completeness vs 58.1 langchain-recursive on 33-doc CLAIR corpus (Wilcoxon p < 0.05). Core MIT is drop-in; gate `[coref]` and `[parsing]` extras. Metrics layer doubles as ground-truth-free chunk eval — cross-ref for [§0.6.0 eval](../roadmap.md#060--eval). |
| **chonkie** ([repo](https://github.com/chonkie-inc/chonkie)) | Chunking library with late-chunking support; token-aware, semantic, and late-interaction modes | MIT | Python + sentence-transformers (optional) | local | **Candidate** — v1.6.7 (2026-05-20), 4k stars. Late-chunking (ColBERT-style) improves dense retrieval for long documents. Gate behind `[semantic]` extra; evaluate against semantic-chunker at §0.4.0. |
| **custom layout-aware** | Tier-split over `CanonicalDoc.root` | n/a (our code) | Python, CPU | local | **Primary** — first-class path; the canonical tree already encodes hierarchy. |

**Notes** — For Quick tier, walking the heading tree replaces external chunkers. External chunkers matter for the Comprehensive RAG-index path. `adaptive-chunking` is the academic-validated picker on top of the rest; its 5 intrinsic metrics are reusable independently of which splitter wins per doc.

## 2. Table / figure extraction (supplemental)

When extraction backends (docling, Kreuzberg) miss or mangle tables/figures.

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **pdfplumber** | Text + tables + bbox from PDFs | MIT | Python + pdfminer.six | local | **Primary (light fallback)** — no native deps beyond pdfminer; lower recall than Camelot but easy default. |
| **Camelot** ([repo](https://github.com/camelot-dev/camelot)) | Lattice + stream table extraction from PDFs | MIT | Python + Ghostscript + OpenCV | local | **Optional** — best lattice recall on born-digital PDFs; Ghostscript native dep. v2.0.0rc1 (2026-05-25, RC stage); active fork at `camelot-dev/camelot` (3.7k stars, last push 2026-05-25). The `atlanhq/camelot-py` fork (NOASSERTION licence, dormant 2023-01-05) is a dead end — do not use. Pin to `camelot-dev/camelot` only. |
| **img2table** | Heuristic table extraction from images and PDFs | Apache-2.0 | Python + OpenCV | local | **Optional** — CPU-only fallback for image/scan paths without GPU. |
| **table-transformer (TATR)** ([repo](https://github.com/microsoft/table-transformer)) | DETR-based table detection + structure recognition | MIT | Python + torch (~1–2 GB) | local (GPU preferred) | **Optional (Comprehensive)** — Microsoft TATR; gate behind `[table-gpu]`. Last push 2024-06-24; last release v1.0.0 (2023). Microsoft repo dormant; HuggingFace weights stable. Do not expect upstream fixes. |
| **marker** ([repo](https://github.com/datalab-to/marker)) | Layout-aware PDF → Markdown with table/figure extraction; hard-deps **surya** ([repo](https://github.com/datalab-to/surya)) for layout detection | **GPL-3.0** (Tier G — see [domain-extraction.md license tier reference](domain-extraction.md#license-tier-reference)) | Python + torch; GPU preferred | PDF, images | **Opt-in (gate)** — marker v1.10.2 (2026-05), 35k stars; surya v0.17.1 (2026-05), 20k stars. Both GPL-3.0. Do not include in default install; gate behind `[marker]` extra. |

**Notes** — Priority: pdfplumber as default → Camelot for lattice precision → img2table for CPU image paths → table-transformer for full Comprehensive accuracy → marker/surya as opt-in-only. None overlap with docling/Kreuzberg's primary role; they are remediation layers.

## 3. Entity extraction / NER

| Tool | Approach | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **spaCy** | Rule + statistical NER, 50+ language models | MIT | Python; models 12–560 MB | local | **Primary** — deterministic, fast, no GPU for `en_core_web_sm/md`. |
| **GLiNER** ([repo](https://github.com/urchade/GLiNER)) | Generative LM-based zero-shot NER | Apache-2.0 | Python + torch (~500 MB) | local | **Candidate (Comprehensive)** — v0.2.26 (2026-05-13), 3k stars. Domain-specific entities without retraining; gate behind `[ner-gliner]`. Siblings: **GLiREL** ([repo](https://github.com/jackboyla/GLiREL)) for zero-shot relation extraction (MIT, v1.2.1, 274 stars); **gliner-multitask** model (HuggingFace: `knowledgator/gliner-multitask-large-v0.5`) for NER + RE + classification in one pass — no separate repo, load via GLiNER library. |
| **Flair** | Contextual string embeddings NER | MIT | Python + torch (300 MB–1 GB) | local | **Avoid** — last release v0.15.1 (2025-10-27), last push 2025-10-27, 14k stars. Superseded by the GLiNER family for this pipeline's zero-shot use case. Drop if GLiNER is adopted; keep only for supervised CoNLL-style models not covered by GLiNER. |
| **outlines** ([repo](https://github.com/dottxt-ai/outlines)) / **outlines-core** ([repo](https://github.com/dottxt-ai/outlines-core)) | Constrained LLM decoding for structured NER | Apache-2.0 | Python + torch + local LLM | local (with local model) | **Candidate (local-LLM)** — core runtime split into `outlines-core` (Apache-2.0, v0.2.14, 291 stars); `outlines` v1.3.0 remains the user-facing package. Pairs with Ollama/vLLM; no cloud calls. |
| **instructor** ([repo](https://github.com/567-labs/instructor)) | Structured output via LLM function-calling | MIT | Python; OpenAI-compatible API | **cloud by default** (local with Ollama/litellm) | **Opt-in only** — v1.15.1 (2026-04-03), 13k stars. v1.x added native `ollama` and `litellm` backends — pointing at local vLLM/Ollama makes this local-compliant. Still gate behind `[ner-llm]` and require explicit endpoint config; default remains cloud. |

**Notes** — Data-locality is the critical axis. spaCy is the safe default. instructor/outlines are the precision ceiling; both require explicit opt-in. Cloud NER calls must be refused under [§0.5.0](../roadmap.md#050--domain-packs) `local-only` profile. instructor v1.x with Ollama/litellm can satisfy `local-only` if endpoint is explicitly set; still requires opt-in gate.

## 4. RAG indexing

Framework vs vector store are orthogonal. Recommended default: LlamaIndex (framework) + Chroma (store) — both Apache-2.0/MIT, embedded, no server.

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **llama-index-core** | RAG framework + ingestion pipeline | MIT | Python | local (LLM calls configurable) | **Primary (framework)** — `VectorStoreIndex` wraps any store. |
| **Haystack (haystack-ai)** ([repo](https://github.com/deepset-ai/haystack)) | RAG pipeline orchestration | Apache-2.0 | Python | local | **Alternative** — v2.29.0 (2026-05-25), 25k stars. v2 is the current API; v1 deprecated upstream. Deeper pipeline graph; prefer LlamaIndex unless consumer already uses Haystack. |
| **Chroma (chromadb)** ([repo](https://github.com/chroma-core/chroma)) | Embedded vector store | Apache-2.0 | Python; optional native HNSW | local | **Primary (store)** — v1.5.9 (2026-05-05), 28k stars. Zero-server, embedded, no Docker. v0.5+ added native BM25 + vector hybrid search — reduces the gap that txtai was filling; reassess txtai candidacy. |
| **Qdrant client** | Client for Qdrant server | Apache-2.0 | Python; needs server or cloud | local server or cloud | **Optional** — better multi-tenant story; overkill for embedded default. |
| **FAISS** | Flat + ANN index | MIT | Python + native (~50 MB CPU) | local | **Candidate** — fastest CPU ANN; less ergonomic than Chroma for metadata filtering. |
| **txtai** | All-in-one embeddings + index + RAG | Apache-2.0 | Python + sentence-transformers | local | **Candidate (light)** — lower integration surface than LlamaIndex. Candidacy weakened by Chroma v0.5+ native BM25 hybrid search. |
| **LightRAG** ([repo](https://github.com/HKUDS/LightRAG)) | Graph-augmented RAG with KG construction | MIT | Python + torch + local/cloud LLM | local (LLM calls configurable) | **Candidate (graph-RAG)** — v1.5.0rc2 (2026-05-25), 36k stars. Pairs vector + graph retrieval; builds entity KG from documents. Evaluate alongside LlamaIndex for §0.5.0 cross-doc graph use cases. |
| **nano-graphrag** ([repo](https://github.com/gusye1234/nano-graphrag)) | Lightweight GraphRAG reference impl | MIT | Python | local | **Candidate (light graph-RAG)** — v0.0.8 (2026-01-27), 4k stars. Simpler alternative to LightRAG for single-domain graph use. |

## 5. Normalization to CanonicalDoc

| Source / tool | What it provides | Gap vs `CanonicalDoc` | License | Verdict |
| --- | --- | --- | --- | --- |
| **docling `DoclingDocument`** ([repo](https://github.com/docling-project/docling)) | Hierarchical doc tree with headings, tables, figures, text blocks; JSON-serializable | Missing `source_sha256`, `built_at`, `tier_summary`; table/figure refs need mapping to `root` leaves | MIT | **Primary normalization source** — richest structural fidelity; thin adapter adds provenance + tier split. v2 changed table/figure serialization mid-2025; review `v2_normalize` adapter and test fixtures against v2.95.0 schema before next release. |
| **docling-core** ([repo](https://github.com/docling-project/docling-core)) | Schema-only sub-package (types, validators, serializers for `DoclingDocument`) split from docling main; Python-native, no torch | No extraction logic; pair with docling for actual normalization | MIT | **Candidate (light import)** — v2.77.0 (2026-05-19), 255 stars. Lighter import for adapters that only need the type definitions without pulling torch; avoids transitive torch dependency at import time in process-stage adapters. |
| **unstructured element schema** | Flat list of typed elements (Title, NarrativeText, Table, Image, …) | No hierarchy; reconstruct from sequence; no provenance | Apache-2.0 | **Secondary** — reconstruct `root` via heading-indent heuristic. Lossier than docling. |
| **Pandoc AST** (via `pypandoc`) | Universal AST; 40+ formats | Pandoc binary GPL; AST is Haskell-native JSON; no provenance | GPL-2+ (Pandoc); MIT (`pypandoc`) | **Optional** — for Office/Markdown/RST sources docling handles poorly. Pandoc binary called as subprocess (does not link), but document the GPL gate. |
| **custom normalizer (in-house)** | Adapter per backend → `CanonicalDoc`; provenance, sha256, tier split baked in | n/a — we own the schema | n/a (our code) | **Required** — load-bearing contract enforcer regardless of upstream source. |

**Notes** — `CanonicalDoc.root` encodes a tree, not a flat list. docling's `DoclingDocument` is the closest existing schema; a thin wrapper adds the four missing fields. `tier_summary` is our invention — no existing tool produces it. The normalizer stage always generates it from `root` via the Quick/Comprehensive tier logic.

- `v2_normalize` reconstructs a flat heading tree from the Kreuzberg-extracted plain text via three regex families (formal-prefix `SECTION`/`SEC.`/`CHAPTER`/`ARTICLE`/`PART`, numbered `5.1 Title`, glued numbered `1Title`) with a 50% density-cap fallback to single-leaf. Real nested hierarchy and docling-based normalize remain deferred to [§0.5.0](../roadmap.md#050--domain-packs) Comprehensive tier.

## 6. Schema-templated extraction

Given a JSON schema template, return JSON conforming to that template. Distinct from §3 NER (entity-span tagging) and from naive prompted-LLM extraction (no schema guarantee). Maps onto `AnalysisReport` (claims, entities, relations, citations) and the structured fields of `CanonicalDoc`.

| Tool | Approach | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **NuExtract3** | 4B VLM fine-tuned for schema-templated extraction (built on Qwen3.5-4B) | Apache-2.0 | Python + transformers; GGUF Q4_K_M ~2.71 GB CPU; ~8 GB VRAM BF16 | local | **Candidate (`external/` benchmark first)** — schema fit for `AnalysisReport` / `CanonicalDoc`; CPU-feasible but seconds-per-doc on Q4. Land as `external/nuextract/run_oneshot.py` benchmark; promote to in-process leg if quality justifies. |
| **outlines** (cross-ref §3) | Constrained decoding over any local LLM | Apache-2.0 | Python + torch + local LLM | local | See §3 — generic constrain-anything path with general-purpose LLMs. |
| **instructor** (cross-ref §3) | Function-calling structured output | MIT | Python; OpenAI-compatible API | cloud-by-default | See §3 — opt-in cloud path; respect `local-only` profile. |

**Notes** — NuExtract3 differentiates by being a *fine-tuned* dedicated extraction model (single weights file), where `outlines + local-LLM` is the *generic-LLM constrained-decoding* path and `instructor` is the *cloud-function-calling* path. NuMind ships a `convert_json_schema_to_nuextract_template()` helper that maps Pydantic schemas to NuExtract templates with a thin type-vocabulary adapter (`verbatim-string` / `date-time` / enums / arrays).

NuExtract3 is a vision-language model — it can read PDFs as images directly, so it overlaps slightly with `Extract` for born-digital and scanned PDFs. The recommended pipeline position is still **downstream of Kreuzberg** (Kreuzberg supplies text+layout; NuExtract3 maps text → schema), but a text-skipping VLM mode is available for scans where Kreuzberg / Tesseract struggle.

Self-reported benchmarks (NuMind, ~600-doc internal set): NuExtract3 at 0.651 vs Qwen3.5-9B at 0.479 and Qwen3.5-4B at 0.417 — outperforms general LLMs ~2× its size on schema-compliance. No independent third-party replication as of 2026-05-25; treat NuMind's published numbers as directional only until an external benchmark confirms them. Promotion to in-process leg should wait for the `external/nuextract/run_oneshot.py` benchmark results.

## What "canonical" means concretely

Three load-bearing claims a `CanonicalDoc` makes that downstream stages rely on:

1. **Provenance is exact** — `source_sha256` is the cryptographic hash of the *bytes* that were extracted; `built_at` is the normalization timestamp. Together these identify which input + which extractor run produced this doc.
2. **`root` is a tree** — heading hierarchy is preserved as nested structure, not as a flat element list. This is what enables tier-aware summarization (Quick = top headings + key claims; Comprehensive = full tree).
3. **`tier_summary` is precomputed** — analysis stages do not re-derive it. This decouples downstream stages from the normalization choice and makes Quick output cheap.

## See also

- [../prototype/plan.md](../prototype/plan.md) — how the chunking, NER, and normalization candidates surveyed here get exercised in the v1 dual-variant prototype.

## Open questions

- Does `CanonicalDoc.root` need a stable node-ID scheme so `AnalysisReport` citations can round-trip back to source nodes?
- Default embedding model for the Chroma/LlamaIndex path — `all-MiniLM-L6-v2` (~80 MB CPU) or larger? Determines whether GPU is required for Comprehensive RAG.
- Should `tier_summary` carry pre-computed entity spans, or are entities always derived at analyze time? Affects whether NER lives in process or analyze.
- Pandoc binary GPL: confirm subprocess invocation (no linking) is acceptable for Apache-2.0 distribution, or gate behind `[pandoc]`.
- Does NuExtract3 deserve its own pipeline leg (`nuextract`) when contracts stabilize in v0.3+, or stay an `external/` benchmark? Decision gated on the benchmark numbers from `external/nuextract/run_oneshot.py` (follow-up).

## References

### Chunking

- langchain-text-splitters: <https://github.com/langchain-ai/langchain/tree/master/libs/text-splitters>
- llama-index node parsers: <https://github.com/run-llama/llama_index>
- semantic-chunker: <https://pypi.org/project/semantic-chunker/>
- unstructured: <https://github.com/Unstructured-IO/unstructured>
- chonkie: <https://github.com/chonkie-inc/chonkie>

### Tables / figures

- pdfplumber: <https://github.com/jsvine/pdfplumber>
- Camelot: <https://github.com/camelot-dev/camelot>
- img2table: <https://github.com/xavctn/img2table>
- table-transformer: <https://github.com/microsoft/table-transformer>
- marker: <https://github.com/datalab-to/marker>
- surya: <https://github.com/datalab-to/surya>

### NER

- spaCy: <https://github.com/explosion/spaCy>
- GLiNER: <https://github.com/urchade/GLiNER>
- GLiREL: <https://github.com/jackboyla/GLiREL>
- Flair: <https://github.com/flairNLP/flair>
- outlines: <https://github.com/dottxt-ai/outlines>
- outlines-core: <https://github.com/dottxt-ai/outlines-core>
- instructor: <https://github.com/567-labs/instructor>

### RAG indexing

- LlamaIndex: <https://github.com/run-llama/llama_index>
- Haystack: <https://github.com/deepset-ai/haystack>
- Chroma: <https://github.com/chroma-core/chroma>
- Qdrant client: <https://github.com/qdrant/qdrant-client>
- FAISS: <https://github.com/facebookresearch/faiss>
- txtai: <https://github.com/neuml/txtai>
- LightRAG: <https://github.com/HKUDS/LightRAG>
- nano-graphrag: <https://github.com/gusye1234/nano-graphrag>

### Normalization

- docling: <https://github.com/docling-project/docling>
- docling-core: <https://github.com/docling-project/docling-core>
- pypandoc: <https://github.com/JessicaTegner/pypandoc>

### Schema-templated extraction

- NuExtract3: <https://huggingface.co/numind/NuExtract3>
- NuExtract3-GGUF: <https://huggingface.co/numind/NuExtract3-GGUF>
- NuMind models: <https://huggingface.co/numind>
