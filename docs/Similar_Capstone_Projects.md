# Similar Capstone / Portfolio Projects (Reference Map for Fuse V2G)

Use these as **architecture references**, not as code to copy wholesale. Closest matches first.

## Complete projects vendored in this repo

Full source trees (runnable references) are under **`reference/`**:

| Local path | Upstream | Use as |
|------------|----------|--------|
| [`reference/rag_application/`](../reference/rag_application/) | [hhphan/rag_application](https://github.com/hhphan/rag_application) | **Primary complete project** — Docker, pgvector, Claude, Streamlit citations, tests |
| [`reference/NeuralStack-RAG/`](../reference/NeuralStack-RAG/) | [harshita-mp/NeuralStack-RAG](https://github.com/harshita-mp/NeuralStack-RAG) | Scheduled ingest + hybrid RAG + citations |

Start with [`reference/README.md`](../reference/README.md) (task ↔ file map + how to run).

---

## Best overall match: scheduled ingest + cited Q&A

### 1. NeuralStack-RAG (strongest structural twin)
**Repo:** https://github.com/harshita-mp/NeuralStack-RAG · **Local:** `reference/NeuralStack-RAG/`  

**What it is:** End-to-end RAG over arXiv papers — automated ingest, hybrid retrieval, Streamlit + FastAPI, answers with `[arxiv_id, section]` citations, **daily scheduled ingest** via n8n.

| Fuse V2G task | What NeuralStack already shows |
|---------------|--------------------------------|
| Discovery / collection | Category-filtered arXiv fetch, idempotent downloads |
| Extraction | PDF parse + section-aware chunking + metadata |
| Storage / vectors | Pinecone + local JSONL for keyword search |
| Classification-ish | LLM query router (methods / experiments / comparison…) |
| RAG + citations | Hybrid BM25 + dense; grounded answers with source ids |
| UI | Streamlit ingest tab + ask tab |
| Schedule | n8n workflow POSTs `/ingest` daily |

**Gap vs Fuse:** Domain is papers, not V2G policy; no jurisdiction/funding labels; weaker on **temporal versioning** (“what changed this month”).

**Steal:** Repo layout (`ingest` / `ask` APIs), citation format, scheduled refresh pattern.

---

### 2. hhphan/rag_application (clean teaching-shaped twin)
**Repo:** https://github.com/hhphan/rag_application  

**What it is:** arXiv → parse → chunk → **Postgres + pgvector** → Claude → **Streamlit with sidebar citations**.

| Fuse need | Fit |
|-----------|-----|
| DB + vectors in one place | Excellent (pgvector matches your plan) |
| Streamlit + citations | Excellent |
| Simple ingest script | Excellent for weeks 1–3 |
| Multi-source policy crawl | No |
| Versioning / change detection | No |

**Steal:** Folder layout (`fetcher`, `parser`, `chunker`, `retriever`, `prompts`, `gui`), Claude + pgvector path (fits Northeastern Claude access).

---

## Closest *domain* matches (energy / EV policy)

### 3. GroundedGrid — U.S. energy policy RAG + RAGAS
**Repo:** https://github.com/RemyAde/GroundedGrid  

**What it is:** RAG over EIA / NREL-style energy documents; Postgres + pgvector; hybrid retrieval; Claude generation; **RAGAS faithfulness / relevancy / context metrics**; compares naive vs hybrid retrieval.

| Fuse need | Fit |
|-----------|-----|
| Energy policy corpus | Strong |
| Phase 3 RAGAS eval | **Strongest match** |
| Hybrid retrieve + rerank | Strong |
| Multi-site scheduled crawl + labels | Partial / in progress |
| Temporal versioning | Not the focus |

**Steal:** Eval harness design (separate judge model from generator), SRS-style requirements doc, metric table for your Phase 3 write-up.

---

### 4. EV-ELM (NREL) — EV policy discover + download + parse
**Repo:** https://github.com/NatLabRockies/EV-ELM  

**What it is:** Research software (not a chat UI): LLM-assisted **discovery and download of EV permitting / policy PDFs**, then parse to structured data (pairs with OEDI dataset).

| Fuse need | Fit |
|-----------|-----|
| Phase 1 discovery / collection | Very strong |
| Terms-aware public policy docs | Strong |
| RAG + Streamlit + citations | Not the product |
| Classification / RAGAS | Downstream, not built-in |

**Steal:** How serious energy labs structure “find policy PDFs → download → parse” pipelines. Use for Task 2–3 design ideas only.

---

### 5. EV-GPT — EV docs + Streamlit + Chroma
**Repo:** https://github.com/nizarkadri/EV-GPT  

**What it is:** Smaller portfolio RAG: EV research PDFs, LangChain, ChromaDB, Gemini, Streamlit, source attribution, Docker.

**Steal:** Minimal demo shape for weeks 10–12 if you need a thin UI reference. Lacks scheduled multi-source ingest and temporal RAG.

---

## Northeastern-shaped RAG capstones (same school / stack culture)

### 6. AskRC — Northeastern Research Computing RAG
**Repo:** https://github.com/Santosh2904/AskRC  

Ingest department docs → Azure search → Streamlit RAG chatbot with traceable sources. Good for **problem framing** (“scattered public docs → cited assistant”) and MLOps/deploy narrative.

### 7. NUBot / AskNEU
- https://github.com/udishadc/NUBot  
- https://github.com/justin-aj/AskNEU  

University-info RAG + Streamlit/React; show scrape → embed → answer patterns. Domain differs; architecture slides are reusable.

### 8. FinSight / earnings RAG (NEU-style coursework)
**Repo:** https://github.com/Snorman-zzz/earnings  

Multi-agent RAG over PDFs, hybrid BM25+vector, verification agent — useful if you want a stronger “don’t hallucinate numbers” story for funding amounts.

---

## Smallest “student FYP” twin (handbook Q&A)

### 9. FYP Handbook Assistant
**Repo:** https://github.com/hashim-i222478/FYP-Handbook-Assistant-RAG-  

`ingest.py` → FAISS → Streamlit → Gemini answers with **(p. X)** citations. Perfect **minimal vertical slice** for your first mock demo (Task 0–5 on one PDF).

---

## Side-by-side: who covers your seven tasks?

| Task | NeuralStack | rag_application | GroundedGrid | EV-ELM | Handbook FYP |
|------|:-----------:|:---------------:|:------------:|:------:|:------------:|
| Kickoff / mocks | △ | ✓ | ✓ | △ | ✓ |
| DB + hash/version | △ | ✓ (pgvector) | ✓ | △ | △ |
| Collect / extract | ✓ (arXiv) | ✓ (arXiv) | ✓ (energy PDFs) | ✓✓ | Single PDF |
| Classification labels | Router only | — | — | Extract fields | — |
| Time-aware RAG | Dates on papers | △ | △ | — | — |
| Streamlit + citations | ✓ | ✓ | API-first | — | ✓ |
| RAGAS / 2-model eval | △ | △ | ✓✓ | — | — |

✓ = solid reference · ✓✓ = best-in-class for that row · △ = partial

---

## What *nobody* fully ships (your differentiator)

These gaps are exactly Fuse’s pitch — lean into them in your report:

1. **Multi-jurisdiction V2G/VGI policy corpus** (CA / BC / California / EU) with an approved source registry + ToS gate  
2. **Temporal versioning** (keep old versions; “what changed last month”)  
3. **Label columns at storage:** Funding / Regulation / Pilot / Research + status  
4. **Weekly change digest** stretch goal  

Your project = NeuralStack’s *pipeline discipline* + GroundedGrid’s *energy + RAGAS* + EV-ELM’s *policy discovery* + handbook project’s *simple Streamlit citations*.

---

## Suggested study order (1–2 days)

1. Skim **hhphan/rag_application** README + folder tree (copy the shape).  
2. Skim **NeuralStack-RAG** ingest + schedule + citation format.  
3. Skim **GroundedGrid** eval / RAGAS plan for Phase 3.  
4. Skim **EV-ELM** only for “how to find EV policy PDFs.”  
5. Clone **FYP Handbook Assistant** and run once — proves your Task 5/6 loop on mocks.

---

## Citation blurb for your proposal / lit review

> Prior student and open projects demonstrate RAG assistants over fixed corpora (handbooks, arXiv, university docs) and emerging energy-document RAG with RAGAS evaluation. Scheduled multi-source ingest with citations appears in systems such as NeuralStack-RAG; energy-policy grounding and automated faithfulness scoring appear in GroundedGrid; EV permitting document discovery appears in NREL EV-ELM. None combine an approved multi-jurisdiction V2G source registry, temporal document versioning for change detection, storage-time policy labels (Funding / Regulation / Pilot / Research), and a cited Streamlit assistant with RAGAS plus comparison to general-purpose chat models — the gap this Fuse capstone addresses.
