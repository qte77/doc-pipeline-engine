---
title: Domain-specific Extraction Models Landscape
purpose: Survey of fine-tuned and domain-pretrained extraction models per industry (biomedical, legal, financial, cybersecurity, ...) for §0.5.0 domain packs and downstream consumers
created: 2026-05-21
updated: 2026-05-26
validated_links: 2026-05-26
category: landscape
---

Survey of **fine-tuned and domain-pretrained extraction models** organised by document domain — biomedical, legal, financial, scientific/patents, cybersecurity, HR, retail, food/agriculture, and others. Distinct from [process.md](process.md) which is *stage-scoped* (chunking, NER, RAG, normalization, schema-templated extraction); this file is *domain-scoped* (which pre-trained models exist for *which kind of document*). Companion files: [ingest.md](ingest.md), [process.md](process.md), [output.md](output.md), [e2e-systems.md](e2e-systems.md).

These models populate `AnalysisReport.entities` / `claims` / `relations` for the per-domain content of [§0.5.0 domain packs](../roadmap.md#050--domain-packs) — `med-research-patents`, `mech-elec-cert`, plus speculative future packs. For domains with **no production-grade fine-tune**, the recommended path is [process.md §6 — schema-templated extraction](process.md#6-schema-templated-extraction) (NuExtract3 + custom Pydantic schemas) instead of waiting for a domain-fine-tuned model.

## Selection criteria

1. **License compatibility** — Apache-2.0 / MIT preferred. CC-BY-SA-4.0 (share-alike) and GPL/LGPL require opt-in extras. CC-BY-NC-4.0 (NonCommercial) and undeclared/`NOASSERTION` licenses block production redistribution. See the [License tier reference](#license-tier-reference) appendix.
2. **Runtime footprint** — Python-native preferred; model size and GPU requirements declared.
3. **Locality** — local-only feasible vs cloud-only. Critical under [§0.5.0](../roadmap.md#050--domain-packs) `local-only` profile.
4. **Adoption signal** — HF downloads > 100/month preferred; GitHub stars > 100 preferred. One-shot research demos with single-digit downloads are not production candidates.
5. **Schema-templated capability** preferred — maps directly to typed `AnalysisReport` fields.

## 1. Biomedical / clinical / pharma

Biomedical document processing requires NER tuned to domain vocabulary (genes, diseases, chemicals, cell lines, species), normalisation to curated ontologies (UMLS, MeSH, NCBI Gene, ChEBI, RxNorm), and relation extraction over clinical notes, PubMed abstracts, and pharmaceutical patents. Outputs populate `AnalysisReport.entities` (typed spans with ontology IDs), `claims` (study findings, drug–disease relations), and `relations` (triples). Locality is critical — clinical text routinely contains PHI; cloud-only tools are blocked under `local-only`. See also [§PHI / de-identification](#phi--de-identification) below.

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **scispaCy** | spaCy pipelines + UMLS/MeSH/HPO/RxNorm entity linkers (`en_ner_bc5cdr_md`, `en_ner_bionlp13cg_md`, `en_ner_craft_md`) | Apache-2.0 | Python + spaCy; models 30–100 MB CPU; UMLS linker ~2.5 GB | local | **Primary** — only Apache-2.0 tool shipping ready UMLS normalisation; v0.6.2 Oct 2025 active. Gate linker behind `[biomed]` extra. |
| **GLiNER-biomed** (`Ihor/gliner-biomed-large-v1.0`) | Zero-/few-shot biomedical NER; DeBERTa-v3-large base; F1 59.77 across 8 datasets | Apache-2.0 (model) / MIT (training repo) | Python + torch; ~400 MB; CPU feasible, GPU preferred | local | **Candidate (Comprehensive)** — zero-shot flex; complements scispaCy. Gate behind `[ner-gliner-biomed]`. |
| **BiomedBERT / PubMedBERT** (`microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext`) | MLM backbone pretrained on PubMed + PMC; top BLURB benchmark | MIT | Python + transformers; ~440 MB | local | **Candidate (fine-tune base)** — not ready-to-use NER; use BENT-* derivatives (`pruas/BENT-PubMedBERT-NER-{Disease,Chemical,Gene}`, Apache-2.0) for out-of-box NER. |
| **d4data/biomedical-ner-all** | DistilBERT fine-tuned on MACCROBAT; 107 biomedical entity classes | Apache-2.0 | Python + transformers; ~250 MB CPU | local | **Optional** — broadest entity vocabulary; ~107 k dl/mo; not normalised to UMLS. |
| **medspaCy** | Clinical pragmatics (negation, section detection, ConText, UMLS linking via scispaCy) | MIT | Python + spaCy + scispaCy | local | **Optional** — essential when negated entities must not populate `entities`. Last push Mar 2026. |
| **HunFlair2** | Flair-based biomedical NER + SapBERT normalisers (disease, gene/protein, chemical, species, cell-line) | Not declared (Flair MIT) | Python + flair ≥0.14; 300 MB–1 GB | local | **Optional** — strong multi-class; license unclear on model card. Lower download velocity (~2.5 k/mo) than scispaCy. |
| **BERN2** | Ensemble biomedical NER + normalisation (OMIM/MeSH/DO/NCBI Gene/DrugBank/dbSNP); REST API mode | BSD-2-Clause | Python + torch; daemon or cloud endpoint | local (with setup) or cloud | **Opt-in (maintenance)** — license compatible but last push Mar 2024 (effectively unmaintained). Use only if OMIM/dbSNP normalisation is required and no alternative exists. |
| **JSL-MedProcNER / JSL Healthcare NLP** | John Snow Labs medical NER (MedProcNER, AnatNER, etc.) | **Commercial (proprietary)** | Python + PySpark (JVM) | n/a | **Avoid** — no OSS counterpart; commercial Healthcare NLP only. Verify before adopting under any "JSL" name. |
| **Spark-NLP OSS core** | Spark NLP annotator ecosystem with LLMEntityExtractor + general/biomedical models | Apache-2.0 | Python + PySpark (JVM); heavyweight | local (cluster) | **Avoid (footprint)** — JVM overhead incompatible with Python-native pipeline. Advanced medical models require JSL commercial. |
| **scispaCy → NuExtract3** (combined path) | scispaCy for NER spans → [process.md §6 NuExtract3](process.md#6-schema-templated-extraction) for schema-templated claims/relations over the same text | Apache-2.0 + Apache-2.0 | See §3 + §6 in process.md | local | **Candidate (Comprehensive, combined)** — two-stage path for `med-research-patents` pack. Natural for `AnalysisReport.{entities,claims,relations}` population. |

**Notes** — scispaCy's `EntityLinker` is the only ready Apache-2.0 UMLS-normalisation path; ~2.5 GB index gated behind `[biomed]`. HunFlair2's SapBERT-based normalisers cover disease/chemical against BC5CDR ontologies via separate per-entity-type downloads. None of the entries de-identify text — see [§PHI](#phi--de-identification). BioBERT (`dmis-lab/biobert`) has no explicit licence and is last-committed 2023; prefer BiomedBERT (MIT) as backbone instead.

## 2. Legal / contracts / regulatory

Legal document processing covers clause extraction (definitions, termination, indemnification, governing law), party and jurisdiction NER, defined-term linking, citation graphs across statutory hierarchies, and regulatory cross-reference resolution. The field splits into **pretrained legal language models** used as backbones and **task-specific fine-tunes** for NER and contract clause QA. Most mature models target English common-law corpora; multilingual coverage is improving but narrower.

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **CUAD-fine-tuned RoBERTa** (`Rakib/roberta-base-on-cuad`, `akdeniz27/roberta-base-cuad`) | Contract clause QA over CUAD (510 US contracts, 41 clause types as QA spans) | MIT | Python + transformers; ~500 MB CPU | local | **Primary (contract clause QA)** — MIT; ~9 k dl/mo; extractive-QA framing maps onto `AnalysisReport.claims`. |
| **en_legal_ner_trf** (`opennyaiorg/en_legal_ner_trf`) | spaCy transformer NER; 14 entity types (COURT, JUDGE, PETITIONER, STATUTE, PRECEDENT, PROVISION, ...); F1 91.1 | Apache-2.0 | Python + spaCy + transformer; ~500 MB | local | **Primary (NER, Indian-law schema)** — Apache-2.0; drops into [process.md §3](process.md#3-entity-extraction--ner) spaCy path; extend label schema for US/EU jurisdictions. |
| **LEGAL-BERT** (`nlpaueb/legal-bert-base-uncased`) | BERT pretrained on 12 GB of mixed English legal text (EURLEX, ECHR, US case law, SEC contracts); 104+ fine-tunes on HF | CC-BY-SA-4.0 | Python + transformers; ~440 MB | local | **Opt-in (CC-BY-SA share-alike)** — 68 k dl/mo, widest adoption. Gate behind `[legal-sa]` extra; share-alike applies to derivative weights/datasets, not inference outputs. |
| **LEGAL-BERT-SMALL** (`nlpaueb/legal-bert-small-uncased`) | Same corpus as LEGAL-BERT, 33% of BERT-BASE size | CC-BY-SA-4.0 | Python + transformers; ~150 MB CPU | local | **Opt-in (CC-BY-SA)** — 18 k dl/mo; fast CPU; same `[legal-sa]` gate. |
| **Legal-Longformer** (`lexlms/legal-longformer-base`) | Continued-pretraining on LeXFiles (19 B tokens, 6 English-speaking legal systems); 4 096-token context | CC-BY-SA-4.0 | Python + transformers; ~500 MB CPU | local | **Opt-in (CC-BY-SA)** — correct architecture for long contracts; only 998 dl/mo. |
| **InLegalBERT / InCaseLawBERT** (`law-ai/InLegalBERT`, `law-ai/InCaseLawBERT`) | BERT pretrained on Indian Supreme Court + High Court judgments (27 GB, 1950–2019) | MIT | Python + transformers; ~440 MB | local | **Candidate** — Indian common-law jurisdiction; 15 k / 900 dl/mo respectively; useful for international/multilingual pipelines. |
| **flair/ner-german-legal** | Flair sequence tagger; 19 German legal entity types; F1 96.35 on LER | Not declared (Flair MIT) | Python + Flair + torch; ~300 MB | local | **Optional (German)** — best-in-class German legal NER; ~10 k dl/mo; verify model-card licence before commercial use. |
| **Saul-7B-Instruct-v1** (`Equall/Saul-7B-Instruct-v1`) | Mistral-7B continued-pretraining on 30 B tokens of legal text; instruction-tuned | MIT | Python + transformers; ~14 GB F16 / ~4 GB Q4 GGUF | local (GPU preferred) | **Candidate (generative)** — Mar 2024; pairs with `outlines`/`instructor` ([process.md §6](process.md#6-schema-templated-extraction)) for constrained schema extraction; CPU-feasible at Q4. |
| **Pile-of-Law LegalBERT-large** (`pile-of-law/legalbert-large-1.7M-2`) | BERT-large trained 1.7 M steps on Pile of Law (256 GB, US federal + state courts + SEC contracts) | **CC-BY-NC-SA-4.0** | Python + transformers; ~1.3 GB | local | **Avoid (NonCommercial)** — NC restriction blocks commercial pipeline; gate explicitly in `[legal-nc]` extra only if research/non-commercial deployment is acceptable. |
| **LexGLUE** (`coastalcph/lex-glue`) | Benchmark framework (7 tasks: ECtHR, SCOTUS, EUR-LEX, LEDGAR, UNFAIR-ToS, CaseHOLD) | CC-BY-4.0 | Python | n/a | **Reference only** — use to score any legal fine-tune. |
| **GLiNER legal fine-tunes** (e.g. `bordias/gliner_legallens_ner`) | GLiNER fine-tunes for legal entities | **GPL-3.0** | Python + torch | local | **Avoid** — GPL-3.0 incompatible with Apache-2.0 redistribution; use OpenNyAI or Saul-7B instead. |

**Notes** — Cleanest Apache-2.0/MIT path: CUAD RoBERTa + OpenNyAI `en_legal_ner_trf` + Saul-7B (when generative needed). LEGAL-BERT family is technically superior but `[legal-sa]` gate is required for downstream consumers. PII redaction is a separate concern; none of these models strip PII — pair with a redaction pass before any cloud-forwarded inference.

## 3. Financial / accounting / SEC

Financial extraction covers sentiment/tone in earnings calls + analyst reports, numeric entity recognition (XBRL tagging) in 10-K/10-Q filings, and full-section structuring of SEC EDGAR filings. General BERT-family models miss financial vocabulary; domain-pretraining on SEC filings or earnings-call corpora measurably improves precision. None handle structured-table extraction natively — they operate on text extracted upstream (Kreuzberg, docling).

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **FinBERT** (`ProsusAI/finbert`) | Sentiment (positive/negative/neutral) on Financial PhraseBank | Apache-2.0 | Python + transformers; ~440 MB | local | **Primary** — 6.6 M dl/mo; safe licence; plug-in `text-classification` pipeline. |
| **FinBERT-Tone** (`yiyanghkust/finbert-tone`) | Tone analysis on 4.9 B-token 10-K/10-Q/earnings-call/analyst corpus | Undeclared on HF card (parent Apache-2.0 — **verify**) | Python + transformers | local | **Opt-in (licence verify)** — 745 k dl/mo; stronger pretraining than ProsusAI; do not redistribute fine-tuned weights until licence confirmed. |
| **SEC-BERT family** (`nlpaueb/sec-bert-base`, `-num`, `-shape`) | BERT pretrained on 260 k 10-K filings (1993–2019); three variants for normal / numeric-masked / numeric-shape tokenisation | CC-BY-SA-4.0 | Python + transformers; ~440 MB | local | **Opt-in (CC-BY-SA)** — best base for XBRL numeric NER fine-tuning; share-alike applies to derivative weights. Gate behind `[finance-sa]`. |
| **FiNER-139** (`nlpaueb/finer-139`) | Financial numeric entity recognition for XBRL tagging; 139-label taxonomy | MIT (repo); weights on HF | Python + transformers | local | **Candidate** — purpose-built for XBRL line-item tagging; niche adoption; validate on target filing format. |
| **FinGPT** (`AI4Finance-Foundation/FinGPT`) | LoRA-adapted LLM fine-tunes (Llama-2/3, Falcon) for financial tasks | MIT | Python + PEFT + base LLM (7B–13B); GPU preferred | local (GPU) | **Opt-in (resource)** — 20 k stars, active. Gate behind `[finance-llm]` due to footprint. |
| **edgar-crawler** (`nlpaueb/edgar-crawler`) | Structured JSON extraction from SEC EDGAR 10-K section items | **GPL-3.0** | Python | local | **Opt-in (subprocess pattern)** — GPL-3.0 incompatible with Apache-2.0 distribution; use as separate process only. |
| **BloombergGPT** | 50B finance-domain LLM trained on Bloomberg's proprietary dataset | Proprietary (no public weights) | Bloomberg Terminal only | cloud-only | **Avoid** — cite as benchmark reference only. |

**Notes** — FinBERT (ProsusAI) is the safe default for sentiment; SEC-BERT-NUM is the recommended base for XBRL numeric NER fine-tuning (under `[finance-sa]`). FinGPT and general-purpose LLMs via `outlines`/`instructor` ([process.md §6](process.md#6-schema-templated-extraction)) cover structured extraction where SEC-BERT encoders lack generation capability. `AlphaResearch` / `RAVEN-Finance` were not found as public models (unverified as of 2026-05-21).

## 4. Scientific / patents / academic

Scientific and patent documents present three distinct workloads: citation graph construction and paper-similarity retrieval (dense embeddings respecting citation proximity), structural parsing of IMRaD sections and reference lists from PDFs, and patent-claim parsing with claim-dependency graphs. The tools below divide along encoder embeddings, structural extraction pipelines, and VLM-based PDF readers.

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **SPECTER2** (`allenai/specter2_base` + adapters) | Task-specific dense embeddings for scientific papers; trained on 6 M+ citation triplets; adapter modules for proximity, query, classification, regression | Apache-2.0 | Python + transformers + adapters; ~500 MB | local | **Primary (embeddings)** — 618 k dl/mo; Apache-2.0; maps onto citation-retrieval in [process.md §4 RAG indexing](process.md#4-rag-indexing). |
| **GROBID** (`kermitt2/grobid`) | Structural extraction from scholarly PDFs: headers, sections, references, citations, affiliations → TEI XML | Apache-2.0 | Java service (Docker); Python client (`grobid-client-python`, Apache-2.0) | local (Docker) | **Primary (academic PDF)** — v0.9.0 Apr 2026, 4.9 k stars; best-in-class reference and section parsing. Gate behind `[grobid]` extra and document Docker requirement. |
| **SciBERT** (`allenai/scibert_scivocab_uncased`) | BERT pretrained on 1.14 M Semantic Scholar papers (3.1 B tokens); scivocab vocabulary | Apache-2.0 | Python + transformers; ~440 MB | local | **Candidate (NER base)** — last push Feb 2022 (stable not archived); superseded by SPECTER2 for retrieval but competitive for scientific NER fine-tuning. |
| **SciSpaCy** (`allenai/scispacy`) | spaCy pipeline + models for scientific/biomedical text | Apache-2.0 | Python + spaCy + model packages (30–300 MB) | local | **Optional** — Apache-2.0; last push Dec 2025; non-biomedical science NER lighter than dedicated biomedical models. Redundant if biomedical pack gates it as Primary. |
| **BERT for Patents** (`anferico/bert-for-patents`) | BERT-LARGE pretrained on 100 M+ patents (multi-jurisdiction); foundation model for patent search and classification | Apache-2.0 | Python + transformers; ~1.3 GB | local | **Candidate** — 14.8 k dl/mo; fill-mask base — fine-tune for claim-boundary NER or hierarchical claim parsing; 26 fine-tuned derivatives on HF. |
| **Nougat** (`facebook/nougat-base`) | VLM: academic PDF images → LaTeX/Markdown via Swin Transformer + mBART; handles math, tables, figures | **CC-BY-NC-4.0** | Python + transformers v4.x (v5+ breaks `image-to-text`); ~1 GB | local (GPU strongly preferred) | **Opt-in (NonCommercial)** — NC blocks commercial use; viable for research pipelines. Note `transformers` v5 compatibility break. |
| **Galactica** (`facebook/galactica-*`) | 125 M–120 B science LLM trained on 106 B tokens of papers + code + chemical compounds | **CC-BY-NC-4.0** | Python + transformers; 30 B+ models GPU only | local (GPU) | **Avoid** — CC-BY-NC-4.0 + known hallucination issues + withdrawn by Meta within days of release. SPECTER2 + GROBID covers retrieval + structure extraction without generation risk. |

**Notes** — GROBID is the structural-extraction anchor for academic PDFs; its Apache-2.0 licence and active 2026 release cadence make it the safe choice despite the Java runtime. SPECTER2 supersedes the original SPECTER (last push Jun 2023) for retrieval. Nougat is uniquely capable for math-heavy PDFs but CC-BY-NC-4.0 gates it. **Patent claim parsing has no mature end-to-end Python-native tool**; recommended path is BERT-for-Patents fine-tuned on claim-boundary data with GLiNER ([process.md §3](process.md#3-entity-extraction--ner)) for zero-shot claim-entity extraction. `CermineDB` was not found as an active maintained project.

## 5. Cybersecurity / threat intelligence

CTI extraction covers five tasks that feed `AnalysisReport.{entities,relations}`: IoC extraction (IPs, domains, hashes, registry keys), CVE/CWE identification and mapping, MITRE ATT&CK technique tagging, threat-actor and campaign entity recognition, and population of STIX 2.1 objects. Domain-pretrained models outperform generic BERT because security text has a specialised vocabulary (CVE IDs, hash strings, ATT&CK technique IDs).

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **cisco-ai/SecureBERT2.0-NER** | NER fine-tune of SecureBERT 2.0 (ModernBERT, 150 M); 5 entity types (Indicator, Malware, Organization, System, Vulnerability); F1 0.945 | Apache-2.0 | Python + transformers; ~600 MB FP32 CPU | local | **Primary** — best-maintained encoder NER for IoC/CVE/malware extraction; 2.95 k dl/mo; published Sep 2025. |
| **oasis-open/cti-python-stix2** | STIX 2.x object creation, parsing, and graph serialisation | BSD-3-Clause | Python; CPU; no model weights | local | **Primary (schema layer)** — canonical Python API for STIX 2.1 bundles; structured-output sink after NER stages. Last push Feb 2026. |
| **fdtn-ai/Foundation-Sec-8B** | Llama-3.1-8B continued-pretraining on ~5.1 B tokens of cybersecurity text (Cisco Foundation AI, Apr 2025); GGUF/Ollama/vLLM quantisations | Apache-2.0 | Python + transformers/vLLM; BF16 ~16 GB VRAM; Q4 GGUF ~4.5 GB RAM | local (GPU recommended) | **Optional (generative path)** — best generative base for schema-templated CTI extraction via `outlines`/`instructor` ([process.md §6](process.md#6-schema-templated-extraction)). |
| **PranavaKailash/CyNER-2.0-DeBERTa-v3-base** | 8-class cybersecurity NER (Indicator, Malware, Organization, System, Vulnerability, Date, Location, Threat Group); F1 91.88 % on CyNER 2.0 | MIT | Python + transformers; 0.2 B FP32 (~800 MB); CPU-feasible | local | **Candidate** — adds Threat Group + Location labels missing from SecureBERT2.0-NER; complements it. |
| **attack-vector/SecureModernBERT-NER** | NER with 22 fine-grained entity types (THREAT-ACTOR, CAMPAIGN, MITRE-TACTIC, CVE, hash variants, REGISTRY-KEYS, IPV4/IPV6, ...); trained on 502 k labelled spans | MIT | Python + transformers; 0.4 B FP32 (~1.6 GB); GPU preferred | local (GPU preferred) | **Candidate (Comprehensive)** — richest entity schema; GPU barrier. Gate behind `[ner-cti-full]`. |
| **jackaduma/SecBERT** | RoBERTa-base pretrained on APTnotes, CASIE, SemEval-2018 Task 8; 84 M params; custom `secvocab` | Apache-2.0 | Python + transformers; ~330 MB CPU | local | **Candidate (NER base)** — 13.7 k dl/mo; predates SecureBERT 2.0; backbone for fine-tuning on private corpora. |
| **markusbayer/CySecBERT** | BERT-base pretrained on cybersecurity text; 110 M params | **Undeclared** | Python + transformers; ~440 MB CPU | local | **Block (licence undeclared)** — 15 k dl/mo (widely used) but no licence field on HF card. Verify before production. |
| **cassandra-anon/CASSANDRA-ASL-TRAM2** | Multi-label ATT&CK technique classifier; 50 ATT&CK sub-techniques; F1 77.17 % on TRAM2 test set | Apache-2.0 | Python + transformers; 110 M; CPU-feasible | local | **Candidate (defer — provenance)** — strongest open ATT&CK technique extractor benchmarked on real CTI reports, but is an **anonymous double-blind peer-review artifact**. Wait for named/versioned release before production. |
| **ioc-finder** (`fhightower/ioc-finder`) | Grammar-based IOC parser (PEG grammars, not regex or ML); extracts IPs, domains, URLs, hashes, CVEs, ASNs, emails | **LGPL-3.0** | Python; CPU; no model weights | local | **Opt-in (LGPL — dynamic linking)** — best grammar-based IOC parser; LGPL-3.0 safe as dynamically-linked import; actively maintained (May 2026). |
| **iocextract** (`inquest/iocextract`) | Regex-based defanged IOC extractor (IPs, URLs, hashes, emails) | **GPL-2.0** | Python; CPU; no model weights | local | **Opt-in (subprocess pattern)** — ubiquitous in CTI tooling but GPL-2.0 requires gate. Prefer `ioc-finder` (LGPL) as primary alternative. |
| **mitre-attack/tram** (v1) | Web app wrapping LogisticRegression classifier over BERT embeddings; maps reports to ATT&CK | Apache-2.0 | Python + Django | local | **Avoid** — unmaintained since Oct 2021; superseded by CASSANDRA/TRAM2 fine-tunes; reference only. |

**Notes** — STIX 2.1 (`cti-python-stix2`) is the output serialisation layer: after NER/technique-tagging, map extracted entities to STIX 2.1 `Indicator`, `Malware`, `Threat-Actor`, `Attack-Pattern` (keyed on ATT&CK technique ID), and `Relationship` objects. Recommended pipeline combines regex IOC pre-pass (high-confidence structured indicators) + ML NER (contextual entity extraction). ATT&CK technique IDs (`T1059.001`) are a controlled vocabulary updated annually by MITRE; classifiers trained on specific framework versions require periodic revalidation.

## 6. HR / résumés / job postings

Use cases: structured resume parsing (name/email/phone/skills/experience/education), job-posting parsing (title/required-skills/experience-level), skill-extraction aligned to ESCO/O*NET ontologies. Outputs populate `AnalysisReport.entities[SKILL, TITLE, COMPANY, INSTITUTION, DEGREE]` and `claims`.

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **`yashpwr/resume-ner-bert-v2`** | BERT; 25 entity types (NAME, EMAIL, PHONE, LOCATION, COMPANY, TITLE, DATE, DEGREE, FIELD, INSTITUTION, SKILL, CERT, LANGUAGE, ...); F1 90.9 % | Apache-2.0 | Python + transformers; ~440 MB CPU | local | **Primary** — 1.5 k dl/mo; 13–25 entity-type variants; Aug 2025. |
| **`oksomu/resume-ner`** | DistilBERT; same 13-entity schema as yashpwr; ONNX artifacts for CPU; F1 97.77 % | Apache-2.0 | Python + transformers / ONNX runtime; ~265 MB | local | **Primary (CPU)** — 157 dl/mo; May 2026 active; ONNX path is the fastest inference option. |
| **`jjzha/jobbert-base-cased`** | MLM backbone pretrained on 3.2 M job-posting sentences (SkillSpan corpus); base for hard/soft skill span extraction | Apache-2.0 (base bert-base-cased; verify card) | Python + transformers; ~440 MB | local | **Candidate (backbone)** — 12 k dl/mo (highest in HR cluster); pair with `jjzha/skillspan-*` fine-tunes for `entities[SKILL]`. |
| **`amosify/distilbert-resume-ner-v1`** | DistilBERT resume NER | Apache-2.0 | Python + transformers; ~265 MB | local | **Optional** — 97 dl/mo; May 2026 active. |
| **`OmkarPathak/pyresparser`** | Python resume parsing library | **GPL-3.0** | Python; CPU; relies on spaCy | local | **Opt-in (subprocess pattern)** — 960 GH stars; widespread but GPL-3.0 blocks Apache-2.0 redistribution. |
| **`DaFull/en_ner_job_postings`** | spaCy model for job-posting entities | MIT | Python + spaCy | local | **Optional** — 3 dl/mo (low adoption) but permissive. |

**Notes** — `oksomu/resume-ner` is the fastest CPU path (ONNX). `jjzha/jobbert-base-cased` is the canonical backbone for skill-extraction fine-tunes (SkillSpan). ESCO / O*NET ontology mapping is a downstream concern — these models output text spans, not ESCO IDs; map spans to ontology codes post-NER. PII concerns apply: resumes carry personal data; same redaction-before-cloud-NER constraint as biomedical PHI.

## 7. Retail / e-commerce

Use cases: product attribute extraction (brand, category, name, material, color, dimensions), product-listing parsing, query understanding for search/discovery. Outputs populate `AnalysisReport.entities[BRAND, CATEGORY, PRODUCT_NAME, ATTRIBUTE, UoM]`.

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **`thepian/product-query-ner`** | BERT-base; 17 entity types: brand, product category, product name, origin, material, color, modifier, UoM, etc. | Apache-2.0 | Python + transformers; ~440 MB CPU | local | **Primary** — 85 dl/mo; Apr 2026 active; production-quality coverage. |
| **`thepian/product-query-ner-int8`** | INT8 quantised sibling | Apache-2.0 | Python + ONNX/transformers; ~110 MB CPU | local | **Primary (CPU)** — 74 dl/mo; CPU-friendly inference. |
| **`xinyangz/OAMine`** | Open-world attribute mining (SIGIR paper); weak-supervision training pipeline; no pre-trained weights, full pipeline | Apache-2.0 | Python | local | **Optional (fine-tune pipeline)** — 31 stars; use when custom attribute schemas needed. |
| **`google-research-datasets/MAVE`** | Dataset (not model): 3 M attribute-value annotations across 1 257 Amazon categories; 2.2 M product profiles | NOASSERTION | n/a | n/a | **Reference (dataset)** — 156 stars; use as fine-tuning corpus; verify per-use licence terms. |
| **`clw8998/Product-Name-NER-model`** | BERT; product name extraction specifically | Apache-2.0 | Python + transformers; ~440 MB CPU | local | **Optional** — 16 dl/mo; Sep 2024; narrower scope than `thepian/product-query-ner`. |

**Notes** — `thepian/product-query-ner` directly populates `AnalysisReport.entities[BRAND, CATEGORY, PRODUCT_NAME, ATTRIBUTE]`. OAMine provides the training pipeline for custom attribute schemas; MAVE provides the corpus. Domain is commercially crowded (vendor APIs) but the OSS fine-tuned-model landscape is sparser than legal/biomedical — `thepian` is the only production-grade open model.

## 8. Agriculture / food / nutrition

Two distinct sub-domains: **food** (recipe ingredients, nutrition-label entities, FoodBase corpus mentions) and **agri-science** (crop varieties, soil properties, FAIR metadata, geospatial fields). Outputs populate `AnalysisReport.entities[FOOD_ITEM, INGREDIENT, CROP, SOIL_PROPERTY, LOCATION, DATE]`.

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **`vladnov138/bert-ner-recipes-by-trainer`** | BERT recipe NER; F1 0.92 | Apache-2.0 | Python + transformers; ~440 MB CPU | local | **Primary (food)** — 476 dl/mo (highest in domain); Apr 2026 active. |
| **`IT-ZBMED/Agriculture_NER_Model_for_FAIR_Metadata_Enrichment`** | XLM-RoBERTa-large (0.6 B); 17 entities (cropSpecies, cropVariety, soilPH, soilTexture, country, region, startTime, ...); en + de; F1 0.76 | MIT | Python + transformers; ~2.4 GB; GPU preferred | local | **Primary (agri-science)** — 370 dl/mo; Dec 2025 active; best multi-entity coverage. |
| **`Dizex/FoodBaseBERT-NER`** | BERT; single FOOD entity from FoodBase corpus | MIT | Python + transformers; ~440 MB | local | **Optional** — 111 dl/mo; narrow single-entity scope. |
| **`carolanderson/roberta-base-food-ner`** | RoBERTa; food mentions in recipes; F1 0.96 | MIT | Python + transformers; ~500 MB | local | **Optional** — 93 dl/mo; compact ~300 hand-labelled recipes corpus. |
| **`davanstrien/deberta-v3-base_fine_tuned_food_ner`** | DeBERTa-v3 food NER; F1 0.94 | MIT | Python + transformers; ~700 MB | local | **Optional** — 86 dl/mo. |
| **`kanak8278/electra-base-ner-food-recipe`** | ELECTRA-base food + recipe combined NER | Apache-2.0 | Python + transformers; ~440 MB | local | **Optional** — 12 dl/mo. |

**Notes** — `vladnov138` is the strongest food/recipe-entity model; `IT-ZBMED` is the strongest agri-science-entity model. Use both for full coverage if the pipeline ingests both recipes and agricultural metadata. Pesticide/fertiliser NER, EU food-labelling extractors, and USDA-aligned models were not found as published OSS fine-tunes — extend via [process.md §6](process.md#6-schema-templated-extraction) with custom schemas.

## 9. Mechanical / electrical engineering / certifications

Use cases: IEC/IEEE/UL/CE/FCC certification metadata, component datasheets, BOM tables, ISO/RoHS/REACH compliance, CAD drawing annotations. The mech-elec-cert pack is on the [§0.5.0 roadmap](../roadmap.md#050--domain-packs).

**Domain landscape: sparse.** Searches across HuggingFace and GitHub found **no production-grade fine-tuned OSS extraction model** with meaningful adoption. The closest pre-training candidates (EnergyBERT, MatSciBERT) are scientific-literature MLMs without extraction heads. **The recommended path is [process.md §6](process.md#6-schema-templated-extraction) (NuExtract3 + custom engineering schemas)** plus the cross-references below.

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **ezdxf** (`mozman/ezdxf`) | CAD/DXF text and attribute extraction (pure Python library, not a model); extracts annotation text and block attributes from `.dxf` / `.dwg` | MIT | Python; CPU | local | **Optional** — only domain-specific tool found; not ML but the canonical Python path for CAD annotation extraction. |
| **EnergyBERT** (`Master-AI-Lab/EnergyBERT`) | BERT MLM pretrained on 1.2 M energy/materials papers — no extraction head | MIT | Python + transformers; 0.1 B params | local | **Candidate (fine-tune base, research)** — last release Jul 2023; requires fine-tuning for any extraction use. |
| **MatSciBERT** (`m3rg-iitd/matscibert`) | BERT MLM for materials science (alloys, cement, composites); 19 community fine-tunes | MIT | Python + transformers; 0.1 B params | local | **Candidate (fine-tune base, research)** — adjacent to mech-elec but not electrical-cert focused. |
| **General-purpose path** | [process.md §2 Table Transformer](process.md#2-table--figure-extraction-supplemental) + [§5 docling normalisation](process.md#5-normalization-to-canonicaldoc) + [§6 NuExtract3](process.md#6-schema-templated-extraction) over custom `CertificateSchema` / `BOMRowSchema` / `DatasheetParamSchema` | Apache-2.0 / MIT | See process.md | local | **Primary (recommended path)** — domain has no fine-tuned model; populate `AnalysisReport` via schema-templated extraction over upstream-extracted text. |

**Notes** — The `pinDef` benchmark (`tk-king/pinDef`, May 2025) demonstrates the research gap: dataset for pin-definition extraction from datasheets, ships no trained model. General-purpose invoice NER models on HF have < 50 dl/mo and stale 2021–2023 dates — not viable. Until a domain-fine-tuned model emerges, the §6 schema-templated path is the production answer.

## 10. Government / regulatory / public-sector

Use cases: regulatory cross-reference extraction (CFR §, FR Vol.), FOIA response parsing, procurement-document parsing (SF-49, FAR, FedConnect), agency-specific entity recognition, EU regulation cross-references. Distinct from §2 Legal (which covers court cases + contracts) — this scope is administrative records, regulatory filings, and government corpora.

**Domain landscape: sparse.** No production-grade `GovBERT` / `FedBERT` / `PolicyBERT` exists with meaningful adoption. EUR-Lex is the only sub-domain with real model coverage, and it overlaps with the legal section. **Primary recommended path is [process.md §6](process.md#6-schema-templated-extraction) (NuExtract3) + [process.md §3](process.md#3-entity-extraction--ner) spaCy rule-based NER for citations + agency names.**

| Tool | Role | License | Runtime | Locality | Verdict |
| --- | --- | --- | --- | --- | --- |
| **EURLEX-BERT** (`nlpaueb/bert-base-uncased-eurlex`) | MLM backbone pretrained on 116 K EU legislative acts | CC-BY-SA-4.0 | Python + transformers; ~440 MB | local | **Opt-in (CC-BY-SA)** — 804 dl/mo; distinct EUR-Lex pretraining vs general LEGAL-BERT. Same `[legal-sa]` gate as the legal pack. |
| **MultiEURLEX** dataset | 65 K EU laws in 23 languages, multi-label EUROVOC classification | Not explicitly declared | n/a (dataset) | n/a | **Reference (benchmark)** — canonical benchmark for EU regulatory topic tagging. |
| **EUR-Lex-Sum** dataset (Aumiller et al. 2022) | Multilingual abstractive summarisation of EU legal acts in up to 24 languages; community BART/T5/MT5 fine-tunes | Dataset: CC-BY-4.0; community fine-tunes: mixed (some CC-BY-NC-SA) | Python + seq2seq transformers | local | **Candidate (dataset + DIY fine-tune)** — use CC-BY-4.0 dataset to train your own; existing community fine-tunes have ≤6 downloads each. |
| **`finetuned-ecfr-embeddings`** (MasterControlAIML) | Sentence-transformer fine-tuned on 500 K eCFR samples for semantic similarity | Not declared (base Apache-2.0) | Python + sentence-transformers; ~420 MB | local | **Candidate (RAG retrieval only)** — useful for eCFR semantic search; not an extraction model. Belongs in [process.md §4 RAG indexing](process.md#4-rag-indexing) cross-references. |
| **spaCy + custom government rules** ([process.md §3](process.md#3-entity-extraction--ner) cross-ref) | spaCy NER with custom entity patterns for agency names, regulation citations (CFR §, FR Vol.), FOIA exemption codes, procurement vehicle IDs | MIT | Python; CPU | local | **Primary (fallback)** — most reliable path for agency/citation/code entity extraction in absence of a production-grade gov-specific model. |
| **NuExtract3** ([process.md §6](process.md#6-schema-templated-extraction) cross-ref) | Schema-templated extraction over government document text | Apache-2.0 | GGUF Q4_K_M ~2.71 GB CPU | local | **Primary (schema extraction)** — no government-specific fine-tune outperforms a general schema model. Define a JSON schema per document type. |

**Notes** — Coverage is jurisdictionally skewed: US-federal (eCFR) and EU-legislative (EUR-Lex) only. UK government / Crown Copyright documents and non-Western regulatory corpora are uncovered. FOIA redaction handling, NSF/NIH funding document NER, census-bulletin extraction, and FAR/FedConnect procurement NER all remain rule-based territory.

## 11. Other domains — notes only

Domains with one or two permissive candidates that don't justify a full subsection.

**News / journalism / media** — `QuantBridge/energy-news-classifier-ner-multitask` (Apache-2.0, 2025) is the best permissive English candidate; 9 entity types (COMPANY, ORG, COUNTRY, COMMODITY, LOCATION, MARKET, EVENT, PERSON, INFRASTRUCTURE). Strong for energy-news contexts; weak for general newswire. `newsmediabias/UnBIAS-NER` (MIT, U Toronto) covers bias-span detection. Modern newswire NER otherwise relies on general-purpose CoNLL-trained models (`dslim/bert-base-NER`, MIT) already adequate for PER/ORG/LOC.

**Insurance / claims** — `JustAdvanceTechonology/bert-fine-tuned-medical-insurance-ner` (Apache-2.0) covers medical-insurance overlap (ICD-10 adjacent); 42 dl/mo. ACORD-form, EOB, and claims-adjudication parsing have no public permissive fine-tuned model. Domain piggybacks on the biomedical pack for ICD-10; full insurance pipeline relies on commercial systems (Guidewire, Duck Creek).

## 12. Domains awaiting fine-tuned models

These domains were searched (deep-sweep methodology in the audit notes) and have **no production-grade permissive fine-tuned extraction model** as of 2026-05-21. The recommended path for all of them is [process.md §6 schema-templated extraction](process.md#6-schema-templated-extraction) with custom domain schemas + general-purpose NER ([process.md §3](process.md#3-entity-extraction--ner)) for span tagging.

- **Real estate / property** — bridge via legal pack (`law-ai/InLegalBERT`) with property-entity extensions; no MLS/lease/deed-specific OSS model with adoption.
- **Education / academic transcripts** — FERPA suppresses public dataset release. Custom annotation against institutional data is the only path.
- **Supply chain / logistics** — bill-of-lading, customs declarations, HS-code extraction are addressed commercially (AWS Textract, Google Document AI) or via private enterprise models.
- **Construction / architecture** — BIM/IFC parsing is geometry territory (IfcOpenShell, pythonocc), not NLP. Construction-spec extraction (CSI MasterFormat, RFI forms) needs custom annotation against AEC corpora.
- **Travel / hospitality** — `facebook/duckling` (Apache-2.0, rule-based, Haskell) covers datetime/duration/location/amount entities from booking confirmations. General-purpose NER + Duckling covers practical use cases without a domain-specific fine-tune.

## PHI / de-identification

**None of the models in this file de-identify text.** For pipelines processing real clinical notes, HR documents containing personal data, or other PHI/PII-bearing sources, a dedicated scrubber must run *before* domain-specific NER. This is a hard requirement under [§0.5.0](../roadmap.md#050--domain-packs) `local-only` profile when source is EHR/hospital data, internal HR systems, or any regulated record.

- **`presidio-analyzer`** (Microsoft, MIT) — Python-native PII detection + de-identification; covers PHI, financial PII, generic PII. Pairs with spaCy backends. Reversibility requires pairing with separate `presidio-anonymizer`.
- **`philter`** (UCSF, BSD-3-Clause) — rule-based clinical-note de-identifier; HIPAA Safe Harbor coverage. Strips data; not reversible.
- **`pseudonymize-text`** ([qte77/pseudonymize-text](https://github.com/qte77/pseudonymize-text), Apache-2.0) — same-governance sibling repo; bulk-pseudonymize names, emails, phones, IBANs, SSNs, credit cards, addresses, organizations across folder trees. **Deterministic** (HMAC-SHA256 + secret key, namespaced per entity type) and **reversible** (mapping file kept separate from output + key). Audit-first two-step CLI: `detect` writes a JSONL plan; `apply` executes byte-identically. GDPR/ENISA/EDPB/NIST framing. Lightweight (stdlib + `python-stdnum` + `phonenumberslite` + Pydantic); optional spaCy via `[ner]` extra. Status: v0.2.0.

All three are pre-NER stage candidates; not currently in the canonical `process.md` stage tables. Consider adding a "de-identification (pre-NER)" subsection to [process.md §3](process.md#3-entity-extraction--ner) once the `§0.5.0 cloud-redacted` deployment profile is wired ([§0.5.0](../roadmap.md#050--domain-packs)). The redactor-default decision was made — `pseudonymize-text` (see [#107](https://github.com/qte77/doc-pipeline-engine/issues/107)); ADR-0012 to be written when the §0.5.0 profile is wired.

## License tier reference

Domain-extraction models surface licence categories that the general-tool landscape files (`ingest.md`, `process.md`, `output.md`) don't see, because fine-tuned domain models commonly ship under share-alike or non-commercial terms. This reference captures the full set used in the verdict columns above.

| Tier | Licences | Treatment | Examples in this file |
| --- | --- | --- | --- |
| **A** | Apache-2.0, MIT | Default. No gating. | scispaCy, SecureBERT2.0-NER, GROBID, SPECTER2, FinBERT, CUAD RoBERTa, `oksomu/resume-ner`, `thepian/product-query-ner` |
| **B** | BSD-2/3-Clause, PSF | Compatible; no gating. | BERN2 (BSD-2), `cti-python-stix2` (BSD-3) |
| **C** | LGPL-2.1, LGPL-3.0 | Safe as dynamically-linked Python import (`from x import ...`). Care needed for static-link distribution. | `ioc-finder` (LGPL-3.0) |
| **D** | CC-BY-SA-4.0 (share-alike) | Share-alike applies to derivative weights/datasets, **not** to inference outputs. Internal use unaffected. Commercial weight redistribution → opt-in extra (`[legal-sa]`, `[finance-sa]`). | LEGAL-BERT, SEC-BERT, EURLEX-BERT |
| **E** | CC-BY-NC-4.0 / CC-BY-NC-SA-4.0 (NonCommercial) | Kills commercial use. Block default; opt-in only for research deployment. | Nougat, Galactica, Pile-of-Law LegalBERT-large |
| **F** | GPL-2.0, GPL-3.0, AGPL-3.0 | Opt-in subprocess only. Cannot link in-process for Apache-2.0 distribution. | `iocextract` (GPL-2.0), `edgar-crawler` (GPL-3.0), `OmkarPathak/pyresparser` (GPL-3.0), GLiNER legal fine-tunes (GPL-3.0) |
| **G** | Undeclared / `NOASSERTION` on HF + GitHub | **Block** until the upstream LICENSE file is read directly and the actual licence confirmed. GitHub's SPDX detector returns `NOASSERTION` for any non-standard licence — including some surprises (e.g. Kreuzberg ELv2 as of v4.8+). | `markusbayer/CySecBERT`, `FinBERT-Tone`, several HF model cards |

**Why a separate tier for "undeclared":** see [issue #76](https://github.com/qte77/doc-pipeline-engine/issues/76) for the Kreuzberg case (MIT → ELv2 upstream relicensing surfaced via direct LICENSE-file inspection after `NOASSERTION` flag). The same pattern bites domain models: assuming an undeclared HF card inherits the base model's licence is wrong often enough that explicit verification is the rule, not an exception.

## See also

- [`../landscape/ingest.md`](ingest.md) — extraction backends + source connectors + crawling.
- [`../landscape/process.md`](process.md) — stage-scoped general tools (chunking, NER, RAG, normalization, schema-templated extraction).
- [`../landscape/output.md`](output.md) — rendering, office formats, templating, conformance.
- [`../landscape/e2e-systems.md`](e2e-systems.md) — end-to-end pipeline systems + USP positioning.
- [`../roadmap.md` §0.5.0](../roadmap.md#050--domain-packs) — domain packs milestone (`med-research-patents`, `mech-elec-cert`).
- [`../prototype/plan.md`](../prototype/plan.md) — how domain-specific candidates exercise in the dual-variant prototype.

## Open questions

- **NuExtract version policy** — current §7 entries reference NuExtract3 (matches [process.md §6](process.md#6-schema-templated-extraction)). NuExtract 2.0 has better adoption signal in some niche use cases. Confirm 3 as the pin target across all sections, or allow 2.0 as a documented fallback.
- **CASSANDRA-ASL-TRAM2 provenance** — currently "Candidate (defer — provenance)" because it is an anonymous double-blind peer-review artifact. Revisit when a named/versioned release lands; risk: production-deploying an artifact that may not be re-released under the same licence.
- **CySecBERT undeclared licence** — 15 k dl/mo of HF traffic on a model with no licence field. Either get upstream to declare or replace with `jackaduma/SecBERT` (Apache-2.0) as the canonical encoder backbone.
- **PHI / de-identification placement** — should `presidio-analyzer` and `philter` get a "de-identification (pre-NER)" subsection in [process.md §3](process.md#3-entity-extraction--ner), or live only as cross-cutting note here?
- **"Other domains" vs "Awaiting" merge** — §11 and §12 carry different information density. Future cycle may merge them with a richer per-domain status row.
- **Adoption-signal floor** — current threshold is "HF dl/mo > 100 OR GH stars > 100". Tighten or relax for the next audit cycle?

## References

### Biomedical

- scispaCy: <https://github.com/allenai/scispacy>
- GLiNER-biomed model card: <https://huggingface.co/Ihor/gliner-biomed-large-v1.0>
- GLiNER-biomed training repo: <https://github.com/ds4dh/GLiNER-biomed>
- HunFlair2 model hub: <https://huggingface.co/hunflair>
- BiomedBERT / PubMedBERT: <https://huggingface.co/microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext>
- BENT-PubMedBERT-NER-Disease: <https://huggingface.co/pruas/BENT-PubMedBERT-NER-Disease>
- d4data/biomedical-ner-all: <https://huggingface.co/d4data/biomedical-ner-all>
- medspaCy: <https://github.com/medspacy/medspacy>
- BERN2: <https://github.com/dmis-lab/bern2>
- Spark-NLP (JSL OSS core): <https://github.com/JohnSnowLabs/spark-nlp>

### Legal

- CUAD: <https://github.com/TheAtticusProject/cuad>
- RoBERTa on CUAD: <https://huggingface.co/Rakib/roberta-base-on-cuad>
- en_legal_ner_trf: <https://huggingface.co/opennyaiorg/en_legal_ner_trf>
- LEGAL-BERT: <https://huggingface.co/nlpaueb/legal-bert-base-uncased>
- LEGAL-BERT-SMALL: <https://huggingface.co/nlpaueb/legal-bert-small-uncased>
- Legal-Longformer: <https://huggingface.co/lexlms/legal-longformer-base>
- InLegalBERT: <https://huggingface.co/law-ai/InLegalBERT>
- InCaseLawBERT: <https://huggingface.co/law-ai/InCaseLawBERT>
- flair/ner-german-legal: <https://huggingface.co/flair/ner-german-legal>
- Saul-7B-Instruct-v1: <https://huggingface.co/Equall/Saul-7B-Instruct-v1>
- Pile-of-Law LegalBERT-large: <https://huggingface.co/pile-of-law/legalbert-large-1.7M-2>
- LexGLUE: <https://github.com/coastalcph/lex-glue>

### Financial

- FinBERT (ProsusAI): <https://huggingface.co/ProsusAI/finbert>
- FinBERT-Tone: <https://huggingface.co/yiyanghkust/finbert-tone>
- SEC-BERT: <https://huggingface.co/nlpaueb/sec-bert-base>
- FiNER-139: <https://github.com/nlpaueb/finer>
- FinGPT: <https://github.com/AI4Finance-Foundation/FinGPT>
- edgar-crawler: <https://github.com/nlpaueb/edgar-crawler>

### Scientific / patents

- SPECTER2: <https://huggingface.co/allenai/specter2_base>
- SciBERT: <https://huggingface.co/allenai/scibert_scivocab_uncased>
- SciSpaCy: <https://github.com/allenai/scispacy>
- GROBID: <https://github.com/kermitt2/grobid>
- GROBID Python client: <https://github.com/lfoppiano/grobid-client-python>
- BERT for Patents: <https://huggingface.co/anferico/bert-for-patents>
- Nougat: <https://huggingface.co/facebook/nougat-base>
- Galactica: <https://huggingface.co/facebook/galactica-30b>

### Cybersecurity

- SecureBERT2.0-NER: <https://huggingface.co/cisco-ai/SecureBERT2.0-NER>
- SecureBERT 2.0 paper: <https://arxiv.org/abs/2510.00240>
- SecureModernBERT-NER: <https://huggingface.co/attack-vector/SecureModernBERT-NER>
- CyNER-2.0-DeBERTa-v3-base: <https://huggingface.co/PranavaKailash/CyNER-2.0-DeBERTa-v3-base>
- jackaduma/SecBERT: <https://huggingface.co/jackaduma/SecBERT>
- CySecBERT (licence undeclared): <https://huggingface.co/markusbayer/CySecBERT>
- CASSANDRA-ASL-TRAM2: <https://huggingface.co/cassandra-anon/CASSANDRA-ASL-TRAM2>
- Foundation-Sec-8B: <https://huggingface.co/fdtn-ai/Foundation-Sec-8B>
- ioc-finder: <https://github.com/fhightower/ioc-finder>
- iocextract: <https://github.com/inquest/iocextract>
- cti-python-stix2: <https://github.com/oasis-open/cti-python-stix2>
- TRAM (v1, unmaintained): <https://github.com/mitre-attack/tram>

### HR / résumés / job postings

- yashpwr/resume-ner-bert-v2: <https://huggingface.co/yashpwr/resume-ner-bert-v2>
- oksomu/resume-ner: <https://huggingface.co/oksomu/resume-ner>
- jjzha/jobbert-base-cased: <https://huggingface.co/jjzha/jobbert-base-cased>
- amosify/distilbert-resume-ner-v1: <https://huggingface.co/amosify/distilbert-resume-ner-v1>
- OmkarPathak/pyresparser (GPL-3.0): <https://github.com/OmkarPathak/pyresparser>
- DaFull/en_ner_job_postings: <https://huggingface.co/DaFull/en_ner_job_postings>

### Retail / e-commerce

- thepian/product-query-ner: <https://huggingface.co/thepian/product-query-ner>
- thepian/product-query-ner-int8: <https://huggingface.co/thepian/product-query-ner-int8>
- xinyangz/OAMine: <https://github.com/xinyangz/OAMine>
- google-research-datasets/MAVE: <https://github.com/google-research-datasets/MAVE>
- clw8998/Product-Name-NER-model: <https://huggingface.co/clw8998/Product-Name-NER-model>

### Agriculture / food

- vladnov138/bert-ner-recipes-by-trainer: <https://huggingface.co/vladnov138/bert-ner-recipes-by-trainer>
- IT-ZBMED/Agriculture_NER_Model_for_FAIR_Metadata_Enrichment: <https://huggingface.co/IT-ZBMED/Agriculture_NER_Model_for_FAIR_Metadata_Enrichment>
- Dizex/FoodBaseBERT-NER: <https://huggingface.co/Dizex/FoodBaseBERT-NER>
- carolanderson/roberta-base-food-ner: <https://huggingface.co/carolanderson/roberta-base-food-ner>
- davanstrien/deberta-v3-base_fine_tuned_food_ner: <https://huggingface.co/davanstrien/deberta-v3-base_fine_tuned_food_ner>
- kanak8278/electra-base-ner-food-recipe: <https://huggingface.co/kanak8278/electra-base-ner-food-recipe>

### Mech-elec-cert

- ezdxf: <https://github.com/mozman/ezdxf>
- EnergyBERT: <https://huggingface.co/Master-AI-Lab/EnergyBERT>
- MatSciBERT: <https://huggingface.co/m3rg-iitd/matscibert>

### Government / regulatory

- EURLEX-BERT: <https://huggingface.co/nlpaueb/bert-base-uncased-eurlex>
- MultiEURLEX dataset: <https://huggingface.co/datasets/Muennighoff/multi_eurlex>
- EUR-Lex-Sum dataset: <https://huggingface.co/datasets/dennlinger/eur-lex-sum>
- finetuned-ecfr-embeddings: <https://huggingface.co/MasterControlAIML/finetuned-ecfr-embeddings>

### Other / awaiting

- QuantBridge/energy-news-classifier-ner-multitask: <https://huggingface.co/QuantBridge/energy-news-classifier-ner-multitask>
- newsmediabias/UnBIAS-NER: <https://huggingface.co/newsmediabias/UnBIAS-NER>
- JustAdvanceTechonology/bert-fine-tuned-medical-insurance-ner: <https://huggingface.co/JustAdvanceTechonology/bert-fine-tuned-medical-insurance-ner>
- facebook/duckling: <https://github.com/facebook/duckling>

### Cross-cutting (PHI / de-id)

- presidio-analyzer: <https://github.com/microsoft/presidio>
- philter: <https://github.com/BCHSI/philter-ucsf>
- pseudonymize-text: <https://github.com/qte77/pseudonymize-text>
