# Prior Art Landscape

End-to-end (E2E) document pipelines for business / enterprise — academic surveys, OSS systems, commercial IDP, and reference architectures. Companion files: [landscape-ingest.md](landscape-ingest.md), [landscape-process.md](landscape-process.md), [landscape-output.md](landscape-output.md).

This file informs USP positioning. It is *not* a buyer's guide.

## Selection criteria

1. **E2E scope** — covers ingest + extract + normalize + analyze + render (or a meaningful subset).
2. **Business / enterprise framing** — production-grade, not just research demo.
3. **Verifiability** — every entry must have a citable URL. No invented projects.
4. **Relevance to a modular embeddable engine** — competitor, inspiration, or orthogonal.

## 1. Academic prior art (arXiv, 2025)

| Paper | What it covers | Relevance |
|---|---|---|
| **Agentic RAG: A Survey** ([arXiv:2501.09136](https://arxiv.org/abs/2501.09136)) | Taxonomy of agentic RAG architectures — agent cardinality, control structure, autonomy, knowledge representation. Names LlamaIndex Agentic Document Workflows as E2E reference. | Maps cleanly to our P1–P4 orchestration patterns; useful taxonomy reference. |
| **RAG: Comprehensive Survey** ([arXiv:2506.00054](https://arxiv.org/abs/2506.00054)) | Adaptive / multi-source / query-refinement / hybrid retrieval families and their trade-offs. | Informs §0.5 RAG indexing choices in [landscape-process.md](landscape-process.md). |
| **Systematic Review of RAG Systems** ([arXiv:2507.18910](https://arxiv.org/abs/2507.18910)) | Multi-library systematic review (ACL, IEEE, ACM, Scholar) through mid-2025. | Coverage map for gaps (eval, governance). |
| **Retrieval And Structuring (RAS)** ([arXiv:2509.10697](https://arxiv.org/abs/2509.10697)) | Argues unstructured-passage RAG is fundamentally limited; integrate structured knowledge (taxonomies, hierarchies, KGs). | Validates our `CanonicalDoc.root` tree (structured, not flat passages). |
| **HetaRAG** ([arXiv:2509.21336](https://arxiv.org/abs/2509.21336)) | Hybrid retrieval across vector + KG + full-text + structured DBs; multimodal (text/diagrams/tables/math). | Reference architecture for cross-store retrieval if `CanonicalDoc` consumers fan out. |
| **AccurateRAG** ([arXiv:2510.02243](https://arxiv.org/abs/2510.02243)) | Local-environment RAG QA framework; PDF-to-text, eval, fine-tuning. | Closest single-paper analog to our "data-locality first" stance. |
| **Modular-RAG taxonomy** ([arXiv:2506.10408](https://arxiv.org/abs/2506.10408)) | Compartmentalises tasks into orchestrated modules (query reformulation, retrieval, ranking, synthesis). | Same modular philosophy as our stage-graph / contracts split. |
| **Engineering the RAG Stack** ([arXiv:2601.05264](https://arxiv.org/html/2601.05264v1)) | Architecture + trust-framework review across retrieval / fusion / modality / trust / adaptivity. | Useful checklist for §0.6 eval. |

## 2. OSS E2E systems

| System | License | E2E scope | Position |
|---|---|---|---|
| **SciPhi-AI / R2R** ([repo](https://github.com/SciPhi-AI/R2R)) | Apache-2.0 | Ingest (PDF/DOCX/MD/MP3/PNG…), chunk, embed, KG extraction, hybrid search, agentic RAG, REST API | **Closest competitor** by feature surface. Difference: R2R is a deployed *service* (REST + Postgres + Docker compose); we are an *embeddable engine* with JSON contracts. |
| **Unstructured.io** ([repo](https://github.com/Unstructured-IO/unstructured)) | Apache-2.0 (OSS core) + commercial API | Ingest + element-typed extraction + chunking; downstream RAG via partner libs | **Adjacent** — already a candidate processor (see [landscape-process.md](landscape-process.md)). Scope is ingest+extract; we cover all five stages with strict contracts. |
| **LlamaIndex + LlamaParse + Agentic Document Workflows** ([LlamaIndex](https://github.com/run-llama/llama_index)) | MIT (LlamaIndex), commercial (LlamaParse) | Parse → index → agentic workflow over docs | **Inspiration, not competitor** — we *use* LlamaIndex as a candidate framework; ADW is one possible orchestration pattern over our stages. |
| **Haystack (deepset)** ([repo](https://github.com/deepset-ai/haystack)) | Apache-2.0 | Pipeline DAG over retriever / reader / generator nodes | **Alternative framework** — graph-based pipeline; heavier than needed for embedded use. |
| **Docling** ([repo](https://github.com/docling-project/docling)) | MIT | Layout-aware extraction → DoclingDocument | **Already wired** as a primary extraction adapter. |
| **AWS GenAI IDP Accelerator** ([repo](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws)) | Apache-2.0 | OCR → Bedrock classify → extract → assess → validate → summarize; SAML/OIDC SSO; private VPC; multi-model | **Vendor-locked competitor** — covers same E2E shape, but tied to AWS Bedrock + CloudFormation/CDK/Terraform. We are cloud-agnostic and embeddable. |
| **AWS Sample IDP Pipeline (multimodal)** ([repo](https://github.com/aws-samples/sample-aws-idp-pipeline)) | Apache-2.0 | Multimodal (PDF/video/audio/image), hybrid search + KG, conversational UI | Reference architecture; explicitly not for production. |
| **AWS aws-ai-intelligent-document-processing** ([repo](https://github.com/aws-samples/aws-ai-intelligent-document-processing)) | Apache-2.0 | Workshop materials + agentic IDP (Analyzer/Matcher/Extractor/Validator/Troubleshooter) | Reference patterns for agent role decomposition. |
| **Document Processing for Regulated Industries** ([repo](https://github.com/aws-samples/document-processing-pipeline-for-regulated-industries)) | Apache-2.0 | Image/PDF processing with lineage and pipeline-ops metadata | Lineage pattern reference for §0.5 audit / `local-only` profile. |
| **thetanishqrathore / IDP** ([repo](https://github.com/thetanishqrathore/IDP)) | Apache-2.0 | RAG-focused: hybrid search (vector + BM25 RRF), context-aware chunking, FastAPI + Qdrant | Solo-maintained; useful as a chunking-strategy reference. |
| **Awesome Document Understanding** ([repo](https://github.com/tstanislawek/awesome-document-understanding)) | CC-BY (typical for awesome-lists) | Curated index of DU / IDP / RPA resources | Discovery aid for further candidates. |

## 3. Commercial IDP (architecture concept only)

Listed for architectural inspiration; not under evaluation as embeddable deps.

- **ABBYY**, **Hyperscience**, **Rossum**, **Instabase** — full-stack IDP suites with proprietary classification and HITL review.
- **Azure AI Document Intelligence** ([docs](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)) — pre-built + custom models; closest cloud equivalent to our extraction tier.
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

1. **Embeddable engine, not a service.** R2R, AWS IDP, Azure DI, Document AI are services. We ship as a Python library with a CLI; orchestrators (polyforge, office-polyforge, Claude Code plugins) embed us — there is no server to run.
2. **Contracts as the public API.** Every stage validates against a JSON schema. The data plane is orchestration-agnostic — any system that can produce/consume the schemas can participate.
3. **Strict license isolation.** Apache-2.0 default; AGPL (PyMuPDF) and JVM (Tika, veraPDF) only as opt-in extras. R2R, Unstructured, and the AWS samples are mostly Apache-2.0 too, but none of them publish a license-isolation policy as a first-class architectural commitment.
4. **Data-locality policies as a contract dimension.** §0.5 will declare `local-only` / `claude-api-extracted-only` / `cloud-redacted` profiles that gate which adapters can load. None of the surveyed systems express this as a runtime policy — they assume cloud or assume local, without an enforced switch.
5. **Domain packs.** §0.5 plans `mech-elec-cert` and `med-research-patents` packs (prompts, thresholds, formats). Reduces the configuration surface for regulated industries.
6. **Two-surface split.** Heavy data plane (Python: extract, validate, render) is decoupled from the optional control plane (skills, agents, hooks). The control plane is replaceable; the data plane is not. Most competitors couple the two.
7. **Output-format conformance contract.** `OutputFormat` + `FormatConformance` formalise what "valid output" means per tier. Most pipelines treat output as best-effort rendering; we treat it as a validated contract.

What competitors *do* better (areas to learn from):

- R2R's REST API surface and Postgres-backed observability — if we ever ship a reference deployment.
- AWS IDP's SAML/OIDC + private VPC story — relevant once enterprise consumers ask.
- LlamaIndex's Agentic Document Workflows — informs the P2/P4 orchestration patterns.
- Unstructured's element-typing taxonomy — useful pre-art when refining the `CanonicalDoc.root` node taxonomy.

## Open questions

- Should we publish a reference deployment (Docker compose) modelled on R2R, or hold the line as a pure library? Trade-off: easier evaluation vs. scope creep into ops.
- Is the `awesome-document-understanding` list worth mining for §0.4 cross-validation samples?
- Does the AccurateRAG paper's local-environment fine-tuning loop belong in §0.6 eval or as a separate domain-pack workflow?
