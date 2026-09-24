import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.retrievers import BM25Retriever
from langchain_core.prompts import ChatPromptTemplate
from ingestion.embedder import get_vectorstore, load_local_chunks

load_dotenv()

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a research assistant answering questions about ML/NLP papers. "
     "Answer ONLY from the provided context. Every claim must cite its source "
     "using the format [arxiv_id, section]. If the context doesn't contain "
     "the answer, say so plainly."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])


def reciprocal_rank_fusion(result_lists, k_constant: int = 60):
    """Merge multiple ranked result lists; docs ranking high in several lists win."""
    scores = {}
    docs_by_key = {}
    for results in result_lists:
        for rank, doc in enumerate(results):
            key = doc.page_content[:100]  # dedupe by content prefix
            docs_by_key[key] = doc
            scores[key] = scores.get(key, 0) + 1 / (k_constant + rank + 1)
    ranked = sorted(scores, key=scores.get, reverse=True)
    return [docs_by_key[key] for key in ranked]


def hybrid_retrieve(question: str, k: int = 5):
    """Run semantic + keyword search, fuse the rankings, return top k."""
    semantic_docs = get_vectorstore().similarity_search(question, k=k)
    bm25 = BM25Retriever.from_documents(load_local_chunks())
    bm25.k = k
    keyword_docs = bm25.invoke(question)
    return reciprocal_rank_fusion([semantic_docs, keyword_docs])[:k]


def format_context(docs):
    parts = []
    for d in docs:
        m = d.metadata
        parts.append(
            f"[arxiv_id: {m.get('arxiv_id')}, section: {m.get('section')}, "
            f"title: {m.get('title')}]\n{d.page_content}"
        )
    return "\n\n---\n\n".join(parts)


def answer_question(question: str, k: int = 5):
    docs = hybrid_retrieve(question, k=k)
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    chain = RAG_PROMPT | llm
    response = chain.invoke({"context": format_context(docs), "question": question})
    sources = [
        {"arxiv_id": d.metadata.get("arxiv_id"), "title": d.metadata.get("title"),
         "section": d.metadata.get("section")}
        for d in docs
    ]
    return {"answer": response.content, "sources": sources}