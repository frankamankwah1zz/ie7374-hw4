# Complete reference projects for Fuse V2G

Two **finished** open projects live here so the team can study a working end-to-end system—not just READMEs.

| Folder | Role | Stack highlight |
|--------|------|-----------------|
| **[`rag_application/`](rag_application/)** | **Primary reference** — complete vertical product | arXiv ingest → Postgres/pgvector → Claude → Streamlit citations + tests + Docker |
| **[`NeuralStack-RAG/`](NeuralStack-RAG/)** | Secondary — scheduled ingest + hybrid RAG | FastAPI + Streamlit + Pinecone + n8n daily job + cited answers |

Provenance: [`ORIGIN.md`](ORIGIN.md).  
**Do not submit this code as your capstone.** Use it to learn structure, then build your own V2G system.

---

## Start here: `rag_application/`

Upstream blog: https://tronghien.com/blog/building-a-rag-pipeline  
Upstream repo: https://github.com/hhphan/rag_application

### What you get (complete pipeline)

```
[arXiv API]
     ↓
[Ingestion]  fetch → parse PDF → chunk (512 tokens)
     ↓
[Embedding]  sentence-transformers → 384-d vectors
     ↓
[PostgreSQL + pgvector]  cosine search
     ↓
[Generation]  Anthropic Claude (grounded prompt)
     ↓
[Streamlit]  chat UI + source citations in sidebar
```

### File → Fuse task map

| Fuse task | Study these files |
|-----------|-------------------|
| **Kickoff / schema** | `src/database/models.py`, `scripts/setup_db.py`, `.env.example` |
| **Database & storage** | `src/database/models.py`, `session.py`, `docker-compose.yml` |
| **Discovery / collection / extraction** | `src/ingestion/fetcher.py`, `parser.py`, `scripts/ingest.py` |
| **Chunking (part of RAG)** | `src/ingestion/chunker.py`, `tests/test_chunker.py` |
| **Time-aware RAG** (adapt: add date/label filters) | `src/embedding/embedder.py`, `src/retrieval/retriever.py`, `tests/test_retriever.py` |
| **UI + answer prompt + citations** | `src/gui/app.py`, `src/generation/prompts.py`, `generator.py` |
| **Evaluation** | Not included — use GroundedGrid / RAGAS for Phase 3 patterns |

### What it does *not* have (you must add for Fuse)

- Multi-source **policy** registry + ToS gate (it uses arXiv only)  
- Label columns: Funding / Regulation / Pilot / Research  
- **Temporal versioning** / change detection  
- RAGAS + Claude vs ChatGPT comparison  
- Weekly digest  

### How to run (local)

```bash
cd reference/rag_application
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set ANTHROPIC_API_KEY
docker compose up -d   # Postgres + pgvector on :5433
# create DB user — see README.md steps 6–7
python scripts/setup_db.py
python scripts/download_model.py
python scripts/ingest.py --category cs.AI --max-results 5
streamlit run src/gui/app.py
```

Full steps: [`rag_application/README.md`](rag_application/README.md).

---

## Secondary: `NeuralStack-RAG/`

Upstream: https://github.com/harshita-mp/NeuralStack-RAG

Use when you need examples of:

- **Scheduled** refresh (`workflows/Daily ArXiv ingestion.json`)  
- Hybrid retrieval + query routing (`retrieval/`)  
- Separate FastAPI backend (`app/main.py`) + Streamlit (`ui/streamlit_app.py`)  
- Citation style `[arxiv_id, section]`  

Run notes: see its README (Pinecone + Groq keys required).

---

## Recommended team exercise (half day)

1. One person runs `rag_application` through ingest → one cited answer.  
2. Walk the code in order: `fetcher → parser → chunker → embedder → retriever → prompts → app`.  
3. On a whiteboard, rewrite the same boxes with **V2G sources**, **label columns**, and **version rows**.  
4. List what you will keep vs replace before Task 1 coding starts.

---

## Suggested ownership while studying

| Person | Focus inside `rag_application` |
|--------|--------------------------------|
| Frank / Isaac | `database/`, `docker-compose.yml`, `setup_db.py` |
| Anahid / Sandeep | `ingestion/`, `scripts/ingest.py` |
| Sandeep | `embedding/`, `retrieval/`, tests |
| Frank | `gui/app.py`, `generation/` |
| Anahid | Note eval gaps → plan RAGAS (Phase 3) |

---

*Parent docs: `docs/Similar_Capstone_Projects.md`, `docs/V2G_Task_Descriptions.md`.*
