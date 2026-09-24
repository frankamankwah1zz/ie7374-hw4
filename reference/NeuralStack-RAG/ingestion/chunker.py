import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Common section headers in ML/NLP papers, in rough order of appearance
SECTION_PATTERNS = [
    ("abstract", r"^\s*abstract\s*$"),
    ("introduction", r"^\s*(\d+\.?\s*)?introduction\s*$"),
    ("related_work", r"^\s*(\d+\.?\s*)?(related\s+work|background)\s*$"),
    ("methods", r"^\s*(\d+\.?\s*)?(method(s|ology)?|approach|model|architecture)\s*$"),
    ("experiments", r"^\s*(\d+\.?\s*)?(experiment(s|al)?( setup)?|evaluation|results?( and discussion)?)\s*$"),
    ("conclusion", r"^\s*(\d+\.?\s*)?(conclusion(s)?|discussion|future\s+work)\s*$"),
    ("references", r"^\s*references\s*$"),
]


def detect_section(line: str, current: str) -> str:
    """If this line looks like a section header, return the new section; else keep current."""
    stripped = line.strip().lower()
    if len(stripped) > 60:  # headers are short; skip normal sentences
        return current
    for section, pattern in SECTION_PATTERNS:
        if re.match(pattern, stripped, flags=re.IGNORECASE):
            return section
    return current


def split_into_sections(pages):
    """Walk through a paper's pages line by line, grouping text by detected section."""
    sections = []  # list of (section_name, text, page_metadata)
    current_section = "front_matter"
    buffer = []
    base_metadata = pages[0].metadata if pages else {}

    for page in pages:
        for line in page.page_content.split("\n"):
            new_section = detect_section(line, current_section)
            if new_section != current_section:
                if buffer:
                    sections.append((current_section, "\n".join(buffer), base_metadata))
                current_section = new_section
                buffer = []
            else:
                buffer.append(line)
    if buffer:
        sections.append((current_section, "\n".join(buffer), base_metadata))
    return sections


def chunk_paper(pages, chunk_size: int = 800, chunk_overlap: int = 120):
    """Section-aware chunking: tag text with its section, then split into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for section_name, text, metadata in split_into_sections(pages):
        if section_name == "references" or not text.strip():
            continue  # bibliography is noise for RAG — skip it
        for doc in splitter.create_documents([text], metadatas=[{**metadata, "section": section_name}]):
            chunks.append(doc)
    return chunks