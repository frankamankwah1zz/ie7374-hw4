import arxiv
import urllib.request
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

DATA_DIR = Path("data")


def fetch_arxiv_papers(query: str = "retrieval augmented generation", max_results: int = 10):
    """Search ArXiv and download paper PDFs into data/. Returns metadata for each paper."""
    DATA_DIR.mkdir(exist_ok=True)
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    papers = []
    for result in client.results(search):
        arxiv_id = result.get_short_id()
        pdf_path = DATA_DIR / f"{arxiv_id.replace('/', '_')}.pdf"
        if not pdf_path.exists():  # skip re-downloading on repeat runs
            urllib.request.urlretrieve(result.pdf_url, str(pdf_path))
        papers.append({
            "arxiv_id": arxiv_id,
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "published": result.published.strftime("%Y-%m-%d"),
            "pdf_path": str(pdf_path),
        })
        print(f"Fetched: {result.title[:70]}")
    return papers


def load_paper(paper: dict):
    """Load one downloaded PDF and attach ArXiv metadata to every page."""
    pages = PyPDFLoader(paper["pdf_path"]).load()
    for page in pages:
        page.metadata.update({
            "arxiv_id": paper["arxiv_id"],
            "title": paper["title"],
            "authors": ", ".join(paper["authors"]),
            "published": paper["published"],
        })
    return pages