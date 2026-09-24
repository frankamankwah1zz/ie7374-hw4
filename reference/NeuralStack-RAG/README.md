# NeuralStack — ArXiv Knowledge Retrieval Pipeline

NeuralStack is an end-to-end agentic RAG (Retrieval-Augmented Generation)
system that automatically ingests ML/NLP research papers from ArXiv and
answers natural-language questions about them with cited, source-grounded
responses. Ask it "How do these papers approach retriever training?" and it
retrieves the relevant passages across its knowledge base and composes an
answer where every claim cites its paper and section.

## Architecture

**Ingestion path:** an n8n workflow (or the Streamlit UI) calls the FastAPI
`/ingest` endpoint → papers are fetched from the ArXiv API → PDFs are parsed
and split by a section-aware chunker that tags each chunk with its paper
section (abstract, methods, experiments, ...) → chunks are embedded locally
with sentence-transformers (384-dim) → vectors and metadata are upserted to
a Pinecone serverless index, with a local JSONL copy kept for keyword search.

**Query path:** a question hits the `/ask` endpoint → an LLM router
classifies it (methods / experiments / metadata / comparison / general) →
a route-specific retrieval strategy runs hybrid search (Pinecone semantic +
BM25 keyword, merged with reciprocal rank fusion) → the top chunks, stamped
with their paper identity, are passed to Llama 3.3 70B on Groq → the model
answers only from the provided context, citing `[arxiv_id, section]` for
every claim.

## Features

- **Automated ArXiv ingestion** — category-filtered queries
  (e.g. `cat:cs.CL AND abs:"retrieval augmented generation"`), idempotent
  downloads, and paper metadata (title, authors, ArXiv ID, date) attached
  to every chunk
- **Section-aware chunking** — pattern-based detection of paper sections so
  retrieval can distinguish a methods passage from a results passage;
  references are dropped as noise
- **Hybrid retrieval** — dense semantic search and BM25 keyword search
  merged with reciprocal rank fusion (implemented from scratch)
- **Agentic query routing** — an LLM pre-classifies each question and the
  retrieval strategy adapts: section re-ranking for methods/experiments
  questions, per-paper diversity caps for cross-paper comparisons
- **Grounded, cited answers** — the model is constrained to the retrieved
  context and declines to answer when the knowledge base lacks relevant
  material (verified with out-of-domain test queries)
- **Scheduled ingestion** — an n8n workflow (exported in `workflows/`)
  POSTs to `/ingest` daily to keep the knowledge base current

## Tech stack

Python · LangChain · HuggingFace sentence-transformers (`bge-small-en-v1.5`)
· Pinecone (serverless) · Llama 3.3 70B via Groq · FastAPI · Streamlit · n8n

## Setup

1. **Clone and create the environment**
```bash
   git clone https://github.com/harshita-mp/NeuralStack-RAG.git
   cd NeuralStack-RAG
   conda create -n neuralstack python=3.12 -y
   conda activate neuralstack
   pip install -r requirements.txt
```

2. **Configure keys** — copy `.env.example` to `.env` and fill in:
   - `GROQ_API_KEY` — free at console.groq.com
   - `PINECONE_API_KEY` — free Starter tier at pinecone.io
   - `PINECONE_INDEX_NAME` — default `neuralstack`

3. **Create the Pinecone index** — serverless, **dimension 384**, metric
   **cosine** (must match the embedding model's output dimension)

4. **Run the backend and UI** (two terminals)
```bash
   uvicorn app.main:app --reload
   streamlit run ui/streamlit_app.py
```

5. Ingest papers from the Streamlit "Ingest papers" tab (or POST to
   `/ingest`), then ask questions. Interactive API docs at
   `http://localhost:8000/docs`.

## Design decisions

- **Local embeddings over an embedding API** — `bge-small-en-v1.5` runs
  free on-device with no rate limits, making 50+ paper ingestion costless;
  the 384-dim output sets the Pinecone index dimension
- **Groq/Llama over paid APIs** — no-card free tier caps worst-case cost
  at zero, which also bounds the risk of public demo usage
- **Hand-rolled RRF over a library ensemble** — version-stable across
  LangChain releases and fully explainable
- **n8n as a thin client** — the workflow only knows the API contract;
  all pipeline logic stays in the application

## Known limitations

- **PDF figure-text contamination** — text inside figures is extracted as
  jumbled fragments and pollutes some chunks; mitigation would be a
  chunk-quality filter or layout-aware parsing
- **No similarity score threshold** — retrieval always returns top-k, so
  irrelevant "sources" appear for unanswerable questions even though the
  model correctly declines to answer
- **Section detection is heuristic** — regex-based header matching covers
  common ML/NLP paper formats (~90%); unusual headers fall through to the
  previous section
- **Local scheduling** — the n8n workflow fires only while n8n runs
  locally; production deployment would use hosted n8n or server-side cron