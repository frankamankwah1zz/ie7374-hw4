import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from retrieval.pipeline import hybrid_retrieve, format_context, RAG_PROMPT
from ingestion.embedder import get_vectorstore

load_dotenv()

ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a query router for a research-paper Q&A system. Classify the "
     "user's question into exactly one route and respond ONLY with JSON, "
     "no other text:\n"
     '{{"route": "<route>", "reason": "<one sentence>"}}\n\n'
     "Routes:\n"
     "- methods: asks how something works, architectures, training, techniques\n"
     "- experiments: asks about datasets, results, metrics, evaluations\n"
     "- metadata: asks about authors, titles, dates, paper identity\n"
     "- comparison: asks to compare or contrast across papers\n"
     "- general: anything else about paper content"),
    ("human", "{question}"),
])

SECTION_ROUTES = {"methods": ["methods"], "experiments": ["experiments"]}


def route_question(question: str) -> dict:
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    raw = (ROUTER_PROMPT | llm).invoke({"question": question}).content
    try:
        return json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
    except json.JSONDecodeError:
        return {"route": "general", "reason": "router output unparseable; defaulting"}


def retrieve_for_route(question: str, route: str, k: int = 5):
    if route in SECTION_ROUTES:
        # Pull a wider net, then prefer chunks from the right sections
        docs = hybrid_retrieve(question, k=k * 3)
        preferred = [d for d in docs if d.metadata.get("section") in SECTION_ROUTES[route]]
        rest = [d for d in docs if d not in preferred]
        return (preferred + rest)[:k]
    if route == "comparison":
        # Need coverage across papers: retrieve more, cap chunks per paper
        docs = hybrid_retrieve(question, k=k * 3)
        per_paper, picked = {}, []
        for d in docs:
            pid = d.metadata.get("arxiv_id")
            if per_paper.get(pid, 0) < 2:
                picked.append(d)
                per_paper[pid] = per_paper.get(pid, 0) + 1
        return picked[:k + 3]
    if route == "metadata":
        # Titles/authors live in every chunk's metadata; a small k suffices
        return get_vectorstore().similarity_search(question, k=3)
    return hybrid_retrieve(question, k=k)


def agentic_answer(question: str, k: int = 5):
    decision = route_question(question)
    docs = retrieve_for_route(question, decision["route"], k=k)
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    response = (RAG_PROMPT | llm).invoke(
        {"context": format_context(docs), "question": question}
    )
    sources, seen = [], set()
    for d in docs:
        key = (d.metadata.get("arxiv_id"), d.metadata.get("section"))
        if key not in seen:
            seen.add(key)
            sources.append({"arxiv_id": key[0], "title": d.metadata.get("title"),
                            "section": key[1]})
    return {"answer": response.content, "route": decision, "sources": sources}