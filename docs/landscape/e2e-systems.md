---
title: E2E Systems Landscape
purpose: End-to-end document pipeline systems and prior art — academic surveys, OSS systems, commercial IDP, reference architectures, gap analysis
created: 2026-04-26
updated: 2026-05-25
validated_links: 2026-05-25
category: landscape
---

End-to-end (E2E) document pipelines for business / enterprise — academic surveys, OSS systems, commercial IDP, and reference architectures. Companion files: [ingest.md](ingest.md), [process.md](process.md), [output.md](output.md), [domain-extraction.md](domain-extraction.md).

This file informs USP positioning. It is *not* a buyer's guide.

## Selection criteria

1. **E2E scope** — covers ingest + extract + normalize + analyze + render (or a meaningful subset).
2. **Business / enterprise framing** — production-grade, not just research demo.
3. **Verifiability** — every entry must have a citable URL. No invented projects.
4. **Relevance to a modular embeddable engine** — competitor, inspiration, or orthogonal.

## 1. Academic prior art (arXiv, 2025)

| Paper | What it covers | Relevance |
| --- | --- | --- |
| **Agentic RAG: A Survey** ([arXiv:2501.09136](https://arxiv.org/abs/2501.09136)) | Taxonomy of agentic RAG architectures — agent cardinality, control structure, autonomy, knowledge representation. Names LlamaIndex Agentic Document Workflows as E2E reference. | Maps cleanly to our P1–P4 orchestration patterns; useful taxonomy reference. |
| **RAG: Comprehensive Survey** ([arXiv:2506.00054](https://arxiv.org/abs/2506.00054)) | Adaptive / multi-source / query-refinement / hybrid retrieval families and their trade-offs. | Informs [§0.5.0](../roadmap.md#050--domain-packs) RAG indexing choices in [process.md](process.md). |
| **Systematic Review of RAG Systems** ([arXiv:2507.18910](https://arxiv.org/abs/2507.18910)) | Multi-library systematic review (ACL, IEEE, ACM, Scholar) through mid-2025. | Coverage map for gaps (eval, governance). |
| **Retrieval And Structuring (RAS)** ([arXiv:2509.10697](https://arxiv.org/abs/2509.10697)) | Argues unstructured-passage RAG is fundamentally limited; integrate structured knowledge (taxonomies, hierarchies, KGs). | Validates our `CanonicalDoc.root` tree (structured, not flat passages). |
| **HetaRAG** ([arXiv:2509.21336](https://arxiv.org/abs/2509.21336)) | Hybrid retrieval across vector + KG + full-text + structured DBs; multimodal (text/diagrams/tables/math). | Reference architecture for cross-store retrieval if `CanonicalDoc` consumers fan out. |
| **AccurateRAG** ([arXiv:2510.02243](https://arxiv.org/abs/2510.02243)) | Local-environment RAG QA framework; PDF-to-text, eval, fine-tuning. | Closest single-paper analog to our "data-locality first" stance. |
| **Modular-RAG taxonomy** ([arXiv:2506.10408](https://arxiv.org/abs/2506.10408)) | Compartmentalises tasks into orchestrated modules (query reformulation, retrieval, ranking, synthesis). | Same modular philosophy as our stage-graph / contracts split. |
| **Engineering the RAG Stack** ([arXiv:2601.05264](https://arxiv.org/html/2601.05264v1)) | Architecture + trust-framework review across retrieval / fusion / modality / trust / adaptivity. | Useful checklist for [§0.6.0](../roadmap.md#060--eval) eval. |

## 2. OSS E2E systems

| System | License | E2E scope | Position |
| --- | --- | --- | --- |
| **SciPhi-AI / R2R** ([repo](https://github.com/SciPhi-AI/R2R)) | **MIT** (changed from Apache-2.0) | Ingest (PDF/DOCX/MD/MP3/PNG…), chunk, embed, KG extraction, hybrid search, agentic RAG, REST API | **Closest competitor (maintenance stall)** — 8k stars. Last commit 2025-11-07; last release v3.6.5 (2025-06-06). Architecture remains the closest competitor by feature surface; velocity has collapsed. R2R is a deployed *service* (REST + Postgres + Docker compose); we are an *embeddable engine* with JSON contracts. R2R stall strengthens claim 1 (embeddable differentiator). |
| **Ontos-AI / Knowhere** ([repo](https://github.com/Ontos-AI/knowhere)) | Apache-2.0 | Parse (MinerU default) → tree-hierarchy reconstruction → multi-modal VLM enrichment (table/image summaries) → cross-doc graph → agentic retrieval (RRF + tree/graph navigation + cited evidence); API + worker + dashboard + Postgres/Redis/S3 via Docker Compose | **Closest competitor (parallel to R2R)** — open-sourced 2026-05-07. Same E2E shape, deployed-service architecture. Cloud LLM/VLM by default (DeepSeek text, Qwen-VL OCR; swappable via env). Their "tree-like hierarchy" maps onto our `CanonicalDoc.root`; multi-modal VLM enrichment + cross-doc graph go beyond our current roadmap. Embeddable-vs-service differentiator (§5.1) and data-locality contract (§5.4) still hold. |
| **Unstructured.io** ([repo](https://github.com/Unstructured-IO/unstructured)) | Apache-2.0 (OSS core) + commercial API | Ingest + element-typed extraction + chunking; downstream RAG via partner libs | **Adjacent** — already a candidate processor (see [process.md](process.md)). Scope is ingest+extract; we cover all five stages with strict contracts. |
| **LlamaIndex + LlamaParse + Agentic Document Workflows** ([LlamaIndex](https://github.com/run-llama/llama_index)) | MIT (LlamaIndex), commercial (LlamaParse) | Parse → index → agentic workflow over docs | **Inspiration, increasingly competitive** — 50k stars, v0.14.22 (2026-05-20). LlamaIndex has rebranded as "the leading document agent and OCR platform"; Agentic Document Workflows increasingly overlap with our E2E scope. We still *use* LlamaIndex as a candidate framework, but its positioning has shifted from pure library toward competitor. Monitor. |
| **Haystack (deepset)** ([repo](https://github.com/deepset-ai/haystack)) | Apache-2.0 | Pipeline DAG over retriever / reader / generator nodes | **Alternative framework** — graph-based pipeline; heavier than needed for embedded use. |
| **Docling** ([repo](https://github.com/docling-project/docling)) | MIT | Layout-aware extraction → DoclingDocument | **Already wired** as a primary extraction adapter. |
| **AWS GenAI IDP Accelerator** ([repo](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws)) | **MIT-0** (changed from Apache-2.0) | OCR → Bedrock classify → extract → assess → validate → summarize; SAML/OIDC SSO; private VPC; multi-model | **Vendor-locked competitor** — 246 stars. Covers same E2E shape, but tied to AWS Bedrock + CloudFormation/CDK/Terraform. We are cloud-agnostic and embeddable. |
| **AWS Sample IDP Pipeline (multimodal)** ([repo](https://github.com/aws-samples/sample-aws-idp-pipeline)) | Amazon Software License (proprietary; GitHub API returns NOASSERTION — confirmed by reading LICENSE) | Multimodal (PDF/video/audio/image); stack: Strands Agents + Step Functions + LanceDB; hybrid search + KG, conversational UI | Reference architecture; explicitly not for production. Note: Amazon Software License is proprietary — cannot redistribute or use as a library dep. |
| **AWS aws-ai-intelligent-document-processing** ([repo](https://github.com/aws-samples/aws-ai-intelligent-document-processing)) | Apache-2.0 | Workshop materials + agentic IDP (Analyzer/Matcher/Extractor/Validator/Troubleshooter) | Reference patterns for agent role decomposition. |
<!-- Removed: aws-samples/document-processing-pipeline-for-regulated-industries — dormant since 2021-10-25 (4+ years stale, 67 stars); no longer a useful reference. -->
| **thetanishqrathore / IDP** ([repo](https://github.com/thetanishqrathore/IDP)) | MIT | Production-grade RAG + Document AI: hybrid search (vector + BM25 RRF), layout-aware chunking, strict citation grounding, Headless API (n8n/Zapier), React UI, FastAPI + Qdrant + Docker | Solo-maintained; last push 2025-12-31. Self-describes as production-grade platform. More substantial than originally noted; useful as a full-stack architecture reference. |
| **Awesome Document Understanding** ([repo](https://github.com/tstanislawek/awesome-document-understanding)) | no licence declared | Curated index of DU / IDP / RPA resources | Discovery aid — dormant since 2023-06-02; 2k stars. Low maintenance; mine for historical candidates only. |
| **DocETL** ([repo](https://github.com/ucbepic/docetl)) | MIT | Agentic LLM pipeline DSL (UC Berkeley EPIC); operators over document collections with LLM-based plan optimization | **Candidate (academic + OSS)** — v0.2.6 (2026-05-20), 4k stars. Direct counterpoint to JSON-contract approach: declarative DSL where LLM chooses operator sequencing. Straddles §1 (academic) and §2 (OSS). |
| **Kreuzberg** ([repo](https://github.com/kreuzberg-dev/kreuzberg)) | Elastic License 2.0 (ELv2; GitHub API returns NOASSERTION — confirmed by reading LICENSE) | Async multi-format extraction facade; covers PDF, Office, images, email, HTML in one API | **Adjacent extraction layer** — v4.9.8 (2026-05-25), 8k stars. Already the primary breadth adapter in [ingest.md §1](ingest.md#1-extraction-backends). ELv2 restricts SaaS redistribution; same Tier-G treatment as documented in ingest.md and [issue #76](https://github.com/qte77/doc-pipeline-engine/issues/76). |

**AWS Strands Agents note** — multiple AWS IDP samples now use Strands Agents as the standard AWS agentic IDP framework (confirmed in sample-aws-idp-pipeline stack above). If an AWS-native orchestration path becomes relevant, Strands Agents is the current AWS reference pattern.

## 3. Commercial IDP (architecture concept only)

Listed for architectural inspiration; not under evaluation as embeddable deps.

- **ABBYY**, **Hyperscience**, **Rossum**, **Instabase** — full-stack IDP suites with proprietary classification and HITL review.
- **Azure AI Document Intelligence** ([docs](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/?view=doc-intel-4.0.0)) — pre-built + custom models; closest cloud equivalent to our extraction tier.
- **AWS Textract / Bedrock Data Automation** — see GenAI IDP Accelerator above.
- **Google Document AI Workbench** ([docs](https://cloud.google.com/document-ai)) — managed extraction + custom processors.

Common traits: vendor lock-in, opaque models, per-page pricing, weak local-only / air-gapped story.

## 4. Reference architectures and engineering blogs

- **AWS — Accelerate IDP with generative AI** ([blog](https://aws.amazon.com/blogs/machine-learning/accelerate-intelligent-document-processing-with-generative-ai-on-aws/)) — narrates the GenAI IDP Accelerator stage graph.
- **Reducto — Document parser comparison** ([page](https://llms.reducto.ai/document-parser-comparison)) — public benchmark across Docling / LlamaParse / Unstructured / Reducto. Vendor-biased but useful.
- **Procycons — PDF Data Extraction Benchmark 2025** — sustainability-report benchmark; Docling ~98% on complex tables, LlamaParse fastest at ~6s/doc, Unstructured strong on simple OCR. (Source URL omitted; bot-protected.)
- **Unstructured benchmark** ([page](https://unstructured.io/blog/unstructured-leads-in-document-parsing-quality-benchmarks-tell-the-full-story)) — vendor-published, biased; useful for the dataset description (scanned invoices, multi-column, nested tables, handwriting).

## 5. Gap analysis — where doc-pipeline-engine fits

What competitors *do not* offer that this project does:

1. **Embeddable engine, not a service.** R2R, AWS IDP, Azure DI, Document AI are services. We ship as a Python library with a CLI; orchestrators (polyforge, office-polyforge, Claude Code plugins) embed us — there is no server to run. *Strengthened* by R2R maintenance stall (last commit 2025-11-07) — the closest service-shaped competitor has stalled.
2. **Contracts as the public API.** Every stage validates against a JSON schema. The data plane is orchestration-agnostic — any system that can produce/consume the schemas can participate.
3. **Strict license isolation.** Apache-2.0 default; AGPL (PyMuPDF), GPL (marker/surya), ELv2 (Kreuzberg), and JVM (Tika, veraPDF) only as opt-in extras. R2R, Unstructured, and the AWS samples are mostly Apache-2.0/MIT too, but none of them publish a license-isolation policy as a first-class architectural commitment.
4. **Data-locality policies as a contract dimension.** [§0.5.0](../roadmap.md#050--domain-packs) will declare `local-only` / `claude-api-extracted-only` / `cloud-redacted` profiles that gate which adapters can load. None of the surveyed systems express this as a runtime policy — they assume cloud or assume local, without an enforced switch.
5. **Domain packs.** [§0.5.0](../roadmap.md#050--domain-packs) plans `mech-elec-cert` and `med-research-patents` packs (prompts, thresholds, formats). *Aspirational until §0.5.0 lands* — no production evidence yet.
6. **Two-surface split.** Heavy data plane (Python: extract, validate, render) is decoupled from the optional control plane (skills, agents, hooks). The control plane is replaceable; the data plane is not. *Under pressure* — Haystack v2 and LlamaIndex Agentic Document Workflows are coupling control and data planes more tightly, narrowing this differentiator.
7. **Output-format conformance contract.** `OutputFormat` + `FormatConformance` formalise what "valid output" means per tier. Most pipelines treat output as best-effort rendering; we treat it as a validated contract.

What competitors *do* better (areas to learn from):

- R2R's REST API surface and Postgres-backed observability — if we ever ship a reference deployment. (Note: R2R stalled; architectural patterns still valid.)
- AWS IDP's SAML/OIDC + private VPC story — relevant once enterprise consumers ask.
- LlamaIndex's Agentic Document Workflows — informs the P2/P4 orchestration patterns.
- Unstructured's element-typing taxonomy — useful pre-art when refining the `CanonicalDoc.root` node taxonomy.
- Knowhere's multi-modal VLM enrichment (table/image summaries linked back to source chunks) + cross-document graph — both go beyond our current `AnalysisReport` shape. Inform [§0.5.0 domain packs](../roadmap.md#050--domain-packs) and any future graph-RAG cross-cut.
- DocETL's declarative DSL + LLM-optimized operator sequencing — reference for §0.5.0 pipeline configuration surface if we expose a user-facing pipeline definition layer.

## See also

- [../prototype/plan.md](../prototype/plan.md) — the v1 dual-variant E2E prototype that operationalizes the gap analysis in this file (Claude Code vs landscape tools, side-by-side eval).

## Open questions

- Should we publish a reference deployment (Docker compose) modelled on R2R, or hold the line as a pure library? Trade-off: easier evaluation vs. scope creep into ops.
- Is the `awesome-document-understanding` list worth mining for [§0.4.0](../roadmap.md#040--adapters) cross-validation samples?
- Does the AccurateRAG paper's local-environment fine-tuning loop belong in [§0.6.0](../roadmap.md#060--eval) eval or as a separate domain-pack workflow?
