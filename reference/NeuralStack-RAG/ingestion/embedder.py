import os
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

load_dotenv()

EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # 384 dimensions — matches our Pinecone index
CHUNKS_FILE = Path("data/chunks.jsonl")


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)


def get_vectorstore():
    return PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX_NAME", "neuralstack"),
        embedding=get_embeddings(),
    )


def upsert_chunks(chunks, batch_size: int = 64):
    """Embed chunks and store them in Pinecone, in batches."""
    store = get_vectorstore()
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        store.add_documents(batch)
        print(f"Upserted {min(i + batch_size, len(chunks))}/{len(chunks)} chunks")
    return len(chunks)


def save_chunks_locally(chunks):
    """Persist chunk text + metadata so BM25 can rebuild without re-ingesting."""
    CHUNKS_FILE.parent.mkdir(exist_ok=True)
    with open(CHUNKS_FILE, "a") as f:
        for c in chunks:
            f.write(json.dumps({"text": c.page_content, "metadata": c.metadata}) + "\n")


def load_local_chunks():
    """Rebuild Document objects from the local chunks file (used by BM25)."""
    docs = []
    with open(CHUNKS_FILE) as f:
        for line in f:
            d = json.loads(line)
            docs.append(Document(page_content=d["text"], metadata=d["metadata"]))
    return docs