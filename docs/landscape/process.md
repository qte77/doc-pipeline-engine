---
title: Process Landscape
purpose: Survey of chunking, table/figure extraction, NER, RAG indexing, schema-templated extraction, and CanonicalDoc normalization for the process stage
created: 2026-04-26
updated: 2026-05-21
validated_links: 2026-05-21
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
| **custom layout-aware** | Tier-split over `CanonicalDoc.root` | n/a (our code) | Python, CPU | local | **Primary** — first-class path; the canonical tree already encodes hierarchy. |

**Notes** — For Quick tier, walking the heading tree replaces external chunkers. External chunkers matter for the Comprehensive RAG-index path.

## 2. Table / figure extraction (supplemental)

When extraction backends (docling, Kreuzberg) miss or mangle tables/figures.

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **pdfplumber** | Text + tables + bbox from PDFs | MIT | Python + pdfminer.six | local | **Primary (light fallback)** — no native deps beyond pdfminer; lower recall than Camelot but easy default. |
| **Camelot** | Lattice + stream table extraction from PDFs | MIT | Python + Ghostscript + OpenCV | local | **Optional** — best lattice recall on born-digital PDFs; Ghostscript native dep. |
| **img2table** | Heuristic table extraction from images and PDFs | Apache-2.0 | Python + OpenCV | local | **Optional** — CPU-only fallback for image/scan paths without GPU. |
| **table-transformer (TATR)** | DETR-based table detection + structure recognition | MIT | Python + torch (~1–2 GB) | local (GPU preferred) | **Optional (Comprehensive)** — Microsoft TATR; gate behind `[table-gpu]`. |

**Notes** — Priority: pdfplumber as default → Camelot for lattice precision → img2table for CPU image paths → table-transformer for full Comprehensive accuracy. None overlap with docling/Kreuzberg's primary role; they are remediation layers.

## 3. Entity extraction / NER

| Tool | Approach | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **spaCy** | Rule + statistical NER, 50+ language models | MIT | Python; models 12–560 MB | local | **Primary** — deterministic, fast, no GPU for `en_core_web_sm/md`. |
| **GLiNER** | Generative LM-based zero-shot NER | Apache-2.0 | Python + torch (~500 MB) | local | **Candidate (Comprehensive)** — domain-specific entities without retraining; gate behind `[ner-gliner]`. |
| **Flair** | Contextual string embeddings NER | MIT | Python + torch (300 MB–1 GB) | local | **Optional** — strong on CoNLL; redundant if GLiNER adopted. |
| **outlines** | Constrained LLM decoding for structured NER | Apache-2.0 | Python + torch + local LLM | local (with local model) | **Candidate (local-LLM)** — pairs with Ollama/vLLM; no cloud calls. |
| **instructor** | Structured output via LLM function-calling | MIT | Python; OpenAI-compatible API | **cloud by default** | **Opt-in only** — violates `local-only` policy unless pointed at local vLLM. Gate behind `[ner-llm]` and require explicit endpoint config. |

**Notes** — Data-locality is the critical axis. spaCy is the safe default. instructor/outlines are the precision ceiling; both require explicit opt-in. Cloud NER calls must be refused under [§0.5.0](../roadmap.md#050--domain-packs) `local-only` profile.

## 4. RAG indexing

Framework vs vector store are orthogonal. Recommended default: LlamaIndex (framework) + Chroma (store) — both Apache-2.0/MIT, embedded, no server.

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **llama-index-core** | RAG framework + ingestion pipeline | MIT | Python | local (LLM calls configurable) | **Primary (framework)** — `VectorStoreIndex` wraps any store. |
| **Haystack (haystack-ai)** | RAG pipeline orchestration | Apache-2.0 | Python | local | **Alternative** — deeper graph; prefer LlamaIndex unless consumer already uses Haystack. |
| **Chroma (chromadb)** | Embedded vector store | Apache-2.0 | Python; optional native HNSW | local | **Primary (store)** — zero-server, embedded, no Docker. |
| **Qdrant client** | Client for Qdrant server | Apache-2.0 | Python; needs server or cloud | local server or cloud | **Optional** — better multi-tenant story; overkill for embedded default. |
| **FAISS** | Flat + ANN index | MIT | Python + native (~50 MB CPU) | local | **Candidate** — fastest CPU ANN; less ergonomic than Chroma for metadata filtering. |
| **txtai** | All-in-one embeddings + index + RAG | Apache-2.0 | Python + sentence-transformers | local | **Candidate (light)** — lower integration surface than LlamaIndex. |

## 5. Normalization to CanonicalDoc

| Source / tool | What it provides | Gap vs `CanonicalDoc` | License | Verdict |
| --- | --- | --- | --- | --- |
| **docling `DoclingDocument`** | Hierarchical doc tree with headings, tables, figures, text blocks; JSON-serializable | Missing `source_sha256`, `built_at`, `tier_summary`; table/figure refs need mapping to `root` leaves | MIT | **Primary normalization source** — richest structural fidelity; thin adapter adds provenance + tier split. |
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

Self-reported benchmarks (NuMind, ~600-doc internal set): NuExtract3 at 0.651 vs Qwen3.5-9B at 0.479 and Qwen3.5-4B at 0.417 — outperforms general LLMs ~2× its size on schema-compliance. No independent third-party replication yet.

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

### Tables / figures

- pdfplumber: <https://github.com/jsvine/pdfplumber>
- Camelot: <https://github.com/camelot-dev/camelot>
- img2table: <https://github.com/xavctn/img2table>
- table-transformer: <https://github.com/microsoft/table-transformer>

### NER

- spaCy: <https://github.com/explosion/spaCy>
- GLiNER: <https://github.com/urchade/GLiNER>
- Flair: <https://github.com/flairNLP/flair>
- outlines: <https://github.com/dottxt-ai/outlines>
- instructor: <https://github.com/567-labs/instructor>

### RAG indexing

- LlamaIndex: <https://github.com/run-llama/llama_index>
- Haystack: <https://github.com/deepset-ai/haystack>
- Chroma: <https://github.com/chroma-core/chroma>
- Qdrant client: <https://github.com/qdrant/qdrant-client>
- FAISS: <https://github.com/facebookresearch/faiss>
- txtai: <https://github.com/neuml/txtai>

### Normalization

- docling: <https://github.com/docling-project/docling>
- pypandoc: <https://github.com/JessicaTegner/pypandoc>

### Schema-templated extraction

- NuExtract3: <https://huggingface.co/numind/NuExtract3>
- NuExtract3-GGUF: <https://huggingface.co/numind/NuExtract3-GGUF>
- NuMind models: <https://huggingface.co/numind>
