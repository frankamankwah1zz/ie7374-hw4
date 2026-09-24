from fastapi import FastAPI
from pydantic import BaseModel
from ingestion.loader import fetch_arxiv_papers, load_paper
from ingestion.chunker import chunk_paper
from ingestion.embedder import upsert_chunks, save_chunks_locally
from retrieval.pipeline import answer_question
from retrieval.agent import agentic_answer

app = FastAPI(
    title="NeuralStack",
    description="Agentic RAG over ArXiv ML/NLP papers",
    version="0.1.0",
)


class IngestRequest(BaseModel):
    query: str = "retrieval augmented generation"
    max_results: int = 10


class AskRequest(BaseModel):
    question: str
    k: int = 5


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest(req: IngestRequest):
    papers = fetch_arxiv_papers(query=req.query, max_results=req.max_results)
    total_chunks = 0
    for p in papers:
        chunks = chunk_paper(load_paper(p))
        save_chunks_locally(chunks)
        upsert_chunks(chunks)
        total_chunks += len(chunks)
    return {
        "papers_ingested": len(papers),
        "chunks_created": total_chunks,
        "titles": [p["title"] for p in papers],
    }


@app.post("/ask")
def ask(req: AskRequest):
    return agentic_answer(req.question, k=req.k)