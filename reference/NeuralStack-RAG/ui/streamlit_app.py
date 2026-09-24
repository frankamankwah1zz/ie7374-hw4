import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="NeuralStack", page_icon="📚", layout="wide")
st.title("NeuralStack — ArXiv Research Assistant")

tab_ask, tab_ingest = st.tabs(["Ask questions", "Ingest papers"])

with tab_ask:
    question = st.text_input("Ask about the ingested papers:",
                             placeholder="How do these papers approach retriever training?")
    k = st.slider("Chunks to retrieve", min_value=3, max_value=10, value=5)
    if st.button("Ask", type="primary") and question:
        with st.spinner("Retrieving and generating..."):
            resp = requests.post(f"{API_URL}/ask", json={"question": question, "k": k})
        if resp.ok:
            data = resp.json()
            st.markdown(data["answer"])
            st.divider()
            st.subheader("Sources")
            seen = set()
            for s in data["sources"]:
                key = (s["arxiv_id"], s["section"])
                if key not in seen:
                    seen.add(key)
                    st.markdown(f"- **{s['title']}** — `{s['arxiv_id']}` ({s['section']})")
        else:
            st.error(f"API error: {resp.status_code}")

with tab_ingest:
    query = st.text_input("ArXiv search query:", value="retrieval augmented generation")
    max_results = st.slider("Number of papers", min_value=1, max_value=25, value=5)
    if st.button("Ingest papers"):
        with st.spinner("Fetching, chunking, embedding... this takes a while"):
            resp = requests.post(f"{API_URL}/ingest",
                                 json={"query": query, "max_results": max_results},
                                 timeout=600)
        if resp.ok:
            data = resp.json()
            st.success(f"Ingested {data['papers_ingested']} papers → {data['chunks_created']} chunks")
            for t in data["titles"]:
                st.markdown(f"- {t}")
        else:
            st.error(f"API error: {resp.status_code}")