# V2G Intelligence Platform — Detailed Task Descriptions

**Aligned with:** *V2G Intelligence Platform Capstone Project Proposal* (Fuse Power Management; revisions from class discussion)  
**Team tasks:** Kickoff → Database → Ingestion → Classification → Time-aware RAG → UI → Evaluation  
**Phases in the proposal:** Phase 1 Ingestion · Phase 2 Retrieval · Phase 3 Evaluation (RAGAS + vs Claude/ChatGPT)

---

## How these tasks map to the proposal

| Your task | Proposal phase | What Fuse cares about |
|-----------|----------------|------------------------|
| Kickoff | Weeks 1–3 setup | Source list, schema, mocks before coding |
| Database & storage | Phase 1 + Temporal RAG | Timestamps, versions, no overwrite |
| Discovery / collection / extraction | Phase 1 | Approved public sources only; multi-format |
| Classification at storage | Phase 1 (revised) | Funding / Regulation / Pilot / Research (+ labels) |
| Time-aware RAG | Phase 2 + Temporal RAG | Chunk → embed → filter by date & labels |
| UI + answer prompt | Phase 2 | Citations: source, URL, date |
| Evaluation | Phase 3 | RAGAS + compare to Claude/ChatGPT |

Phases **1 and 2 run in parallel** after kickoff: RAG starts on mock documents while collectors fill the real corpus.

---

## Task 1 — Kickoff: schema, sources, stack, mocks

### Purpose

Lock shared decisions so the four later workstreams do not diverge. This is the **contract** for the whole project.

### What you do in detail

**1. Document schema (including label columns)**  
Agree every field that will live on a stored document. Minimum from the proposal:

- **Provenance:** source name, URL, publication date, jurisdiction  
- **Content:** raw artifact reference, extracted plain text  
- **Change detection:** content hash, version / timestamp (do **not** overwrite old versions — required for Temporal RAG)  
- **Label columns** (filled later by classification, but defined now):  
  - `doc_type` — proposal categories: **Funding, Regulation, Pilot, Research** (plus `Other` if needed)  
  - `jurisdiction` — e.g. Canada, BC, California, US, EU, multi  
  - `v2g_relevant` — yes/no (filter noise)  
  - `status` — e.g. open / closed / proposed / active / unknown (critical for “currently open” funding questions)  
  - `confidence` — classifier confidence 0–1  

Write this as a one-page schema table or SQL draft everyone signs off on.

**2. Source list**  
Start from Fuse’s trusted list (associations, government/utility sites, standards bodies, research). Students may propose additions. For each source record:

- Name, base URL, jurisdiction, type  
- Whether **terms of use / robots** allow automated access (`allowed_to_fetch`)  
- Notes on format (HTML, PDF, Excel)

MVP uses a **reduced** list (recommend 5–8). Do not scrape paywalled or ToS-blocked sites.

**3. Tech stack**  
Pick boring defaults that fit the $500 cap and “no training” constraint, e.g.:

- Python; Postgres or SQLite; Chroma or pgvector  
- Embeddings + LLM via Fuse / Northeastern Claude credits  
- Streamlit for UI; GitHub Actions or simple cron for schedule later  

**4. Create 15–20 mock documents**  
Hand-authored or lightly edited public snippets that cover:

- Open vs closed **Funding** in Canada  
- **Pilot** in BC and in California (for comparison questions)  
- One **Regulation** / tariff-like note  
- One **Research** blurb  
- One off-topic doc (`v2g_relevant=false`)  
- Mixed “publish dates” so temporal queries have something to filter  

Mocks unblock database, RAG, and UI before real crawlers work.

### Deliverables

- Schema doc (fields + enums)  
- `sources.yaml` v1 with access notes  
- Agreed stack list  
- `mocks/` folder (15–20 files) + short index of what each mock is for  

### Done when

Database owners can create tables; ingest owners know which URLs to hit; RAG/UI owners can build against mocks.

### Proposal questions this enables later

Mocks should already support dry-runs of: funding in Canada; BC vs California; “what changed” using different dates.

---

## Task 2 — Database and storage: schema, raw text, hash, versioning

### Purpose

Own the **persistent corpus**. This is what makes the system reproducible, citable, and able to detect change — the four reasons the proposal rejects one-off ChatGPT search.

### What you do in detail

**1. Implement the agreed schema**  
Tables such as `sources` and `documents` (optional `document_versions` if versions are separate rows). Every document row stores:

- Metadata: source, URL, `published_at`, `fetched_at`, jurisdiction  
- `raw` pointer (file path / blob id) and `text` (extracted)  
- Label columns (nullable until classification runs)  

**2. Raw text storage**  
Keep both:

- **Raw** original (HTML/PDF/Excel bytes or path) for audit and re-parse  
- **Extracted text** used for classification and chunking  

**3. Content hash**  
Compute a stable hash (e.g. SHA-256 of normalized extracted text + canonical URL). Same hash → document unchanged. Different hash → content changed.

**4. Versioning for change detection (Temporal RAG)**  
Per the revised proposal: **store with timestamps instead of overwriting**.

Recommended behavior:

- First see URL → version 1  
- Same URL, new hash → insert version 2 (keep version 1)  
- Queries can ask “as of date” or “what changed since date” by comparing versions / `fetched_at`  

This is the backbone of “What has changed in the last month?” and the weekly digest stretch goal.

**5. Access API for teammates**  
Small functions everyone uses:

- `upsert_document(...)`  
- `list_documents(filters)` — by jurisdiction, doc_type, date range, version  
- `get_document(id)`  
- Optional: `export_jsonl()` snapshot for evaluation  

### Deliverables

- Migrations / `schema.sql`  
- Repository module + tests for hash/version behavior  
- DB seeded with the 15–20 mocks  

### Done when

- Re-ingesting an unchanged page does not create junk duplicates  
- Changing mock text creates a new version  
- “Documents since DATE” is a simple query  

### Risks to manage

Missing publication dates → store `published_at` nullable and always keep `fetched_at` for citations (“retrieved on …”).

---

## Task 3 — Discovery, collection, and text extraction

### Purpose

Phase 1 pipeline body: **discover → collect → extract → (later classify) → store**. Turn the approved source list into a living knowledge base.

### What you do in detail

**1. Source registry**  
Code reads `sources.yaml`. Only sources with `allowed_to_fetch: true` run. Log why others were skipped (terms).

**2. Discovery**  
For each source, find candidate document URLs (listing pages, sitemaps, RSS if available, known PDF links). Stay inside the approved domain/path patterns.

**3. Collection**  
Download with polite rate limits and clear User-Agent. Save raw bytes. Handle HTML pages, PDFs, and Excel (Fuse supplies multi-format samples for testing).

**4. Terms check**  
Before enabling a source: read robots.txt / terms. Document the decision in the registry. Public sources only; no Fuse internal systems; capped API keys in a separate project account.

**5. Text extraction**  
- HTML → main content text (strip nav/boilerplate)  
- PDF → text (pypdf / pdfplumber)  
- Excel → tables normalized into readable text  

Write `text`, metadata, and hash into the DB via Task 2’s API.

**6. Scheduling (capacity)**  
Proposal weeks 4–6: run on a schedule. MVP can start as a manual CLI (`ingest run --source …`) and add cron/GitHub Actions once stable.

### Deliverables

- Collectors for a reduced set (target ≥5 sources for MVP)  
- Extractors with tests on Fuse sample PDF/Excel  
- Run logs (success / skip / error per URL)  
- Optional scheduler  

### Done when

Re-running ingest is idempotent; new pages appear as new docs; changed pages bump versions; teammates can query real rows, not only mocks.

### Out of scope

Fighting CAPTCHAs, paywalled journal PDFs, unrestricted open-web crawl.

---

## Task 4 — Classification at storage

### Purpose

Revised proposal: classify documents into categories to support **filtered retrieval** and **trend tracking**. Labels are **columns on the document**, not buried in free text.

### What you do in detail

**1. When it runs**  
On each **new or changed** document (hash/version trigger). Do not re-classify unchanged hashes (saves the $280 LLM budget).

**2. What the prompt outputs** (saved as columns)

| Column | Meaning | Proposal link |
|--------|---------|---------------|
| `doc_type` | **Funding / Regulation / Pilot / Research** (+ Other) | Classification revision |
| `jurisdiction` | Geographic scope | Metadata requirement |
| `v2g_relevant` | Keep / drop from V2G answers | Quality filter |
| `status` | open / closed / active / proposed / unknown | “Currently open” funding Q |
| `confidence` | 0–1 | Human review threshold |

Also store `classified_at` and prompt/model version for audit.

**3. How**  
LLM prompt over title + truncated text (full text only if needed). Low confidence → `status=unknown` or `doc_type=Other`, still retrievable but filterable.

**4. Spot-check**  
Calibrate on ~10 real docs; adjust prompt; backfill the corpus.

### Deliverables

- `classify_document(doc) → labels`  
- Batch backfill job  
- Short calibration notes  

### Done when

Most docs have sensible `doc_type` + jurisdiction; RAG can filter e.g. `doc_type=Funding` AND `jurisdiction=Canada` AND `status=open`.

### Why it matters for demo questions

- “Funding … currently open in Canada” needs **Funding + Canada + open**  
- “BC vs California” needs jurisdiction labels  
- Trend / digest needs doc_type over time  

---

## Task 5 — Time-aware RAG

### Purpose

Phase 2 retrieval layer, built by the team (not a black-box agent): **chunking, embedding, vector storage, retrieval, generation** — with **temporal** and **label** filters so the corpus is not a flat bag of text.

### What you do in detail

**1. Chunking**  
Split `text` into overlapping chunks. Attach metadata to **every** chunk:

- `doc_id`, `version`, title, URL  
- `published_at` / `fetched_at`  
- `jurisdiction`, `doc_type`, `status`  

**2. Embedding + vector store**  
Embed chunks into Chroma/pgvector (within ~$50 line). **Skip re-embed** if content hash unchanged.

**3. Retrieval with filters**  
Given a user question (and optional UI filters):

- Vector search top-k  
- Restrict by date range (“last month”), jurisdiction, doc_type, status  
- Prefer newer versions when the same URL has multiple versions, unless the user asks for historical “as of”  

This implements **Temporal RAG / Versioning** from the proposal: the system can answer with time context, not only semantic similarity.

**4. Hand-off to generation**  
Return chunks with citation fields ready for the UI prompt (source, URL, date).

**5. Rebuild command**  
After bulk ingest/classify, re-index safely.

### Deliverables

- `index_documents()` / `retrieve(query, filters) → chunks`  
- Config for chunk size, top-k  
- Smoke tests on the three proposal questions using mocks, then real docs  

### Done when

- Canada funding queries retrieve Canadian funding chunks  
- Date filters exclude stale closed programs when asking “currently open”  
- Empty retrieval is possible (UI must then refuse)  

### Design rule

Never rely on the LLM’s training knowledge for V2G facts; only retrieved chunks.

---

## Task 6 — UI (Streamlit) and answer prompt

### Purpose

Phase 2 interface: plain-language questions → **grounded answers with citations and dates**. Streamlit is explicitly sufficient.

### What you do in detail

**1. UI**  

- Question input  
- Optional filters: jurisdiction, doc_type, date range  
- Answer panel  
- Citations panel: **source name, URL, date** (and doc_type if useful)  
- Banner: “Corpus as of {latest fetched_at}”  

**2. Answer prompt (grounding rules)**  

- Use **only** retrieved chunks  
- Every material claim cites source + URL + date  
- If evidence is missing → say **not in corpus** (do not invent funding programs)  
- If sources conflict → state both and prefer newer dated evidence  
- Align tone with Fuse use case: answers may support funding applications / utility submissions → provenance matters  

**3. Logging**  
Save question, retrieved chunk ids, answer, model id — feeds Evaluation.

**4. Parallel build**  
Start with mock retrieval stub; switch to Task 5 API when ready.

### Deliverables

- Runnable Streamlit app  
- Versioned prompt template  
- Demo screenshots for Fuse check-ins  

### Done when

A teammate can ask the three proposal questions and see clickable/pasteable citations; refusal works on “not in corpus” questions.

---

## Task 7 — Evaluation (~30 questions, accuracy, citations, 2 models)

### Purpose

**Phase 3** in the revised proposal: prove the system is trustworthy — not only “it demos well.”

### What you do in detail

**1. Build ~30 test questions**  
Cover the proposal’s intent and edge cases:

| Bucket | Examples | Why |
|--------|----------|-----|
| Funding / open now | “What V2G funding is open in Canada?” | status + jurisdiction |
| Comparison | “How do BC and California V2G programs compare?” | multi-doc |
| Temporal | “What has changed in the last month?” | versioning |
| Filtered type | Regulation / Pilot / Research only | classification |
| Not in corpus | Questions you know are unsupported | anti-hallucination |
| Citation traps | Answers that need a specific URL/date | provenance |

For each: notes on expected sources / acceptable answer points / must-refuse flag.

**2. Answer accuracy (human or rubric)**  
Score whether the answer is correct **given the corpus** (not given the open web).

**3. Citation checks**  

- Citation **present**  
- Citation **correct** (URL/chunk actually supports the claim)  
- Date shown and not invented  

**4. RAGAS framework (proposal Phase 3)**  
Automate where possible:

| Proposal metric | What to measure |
|-----------------|-----------------|
| Relevancy score | Output matches query intent |
| Hallucination rate | Claims unsupported by retrieved context (faithfulness) |
| Answer relevance | Addresses the question |
| Context utilization | Uses retrieved context well (context relevance / precision) |

Run RAGAS on logged Q&A pairs whenever you change prompts, chunking, or models — treat it as a **scorecard**, not a replacement for reading failures. Your PDFs are longer/messier than Wikipedia-style benchmarks, so spot-check by hand.

**5. Comparative testing (two models)**  
Revised proposal: after the system is built, **compare performance against Claude/ChatGPT**.

Practical design (pick and document one):

- **A.** Same RAG pipeline, two generator models (e.g. Claude vs GPT) — fair test of generation  
- **B.** Your full system (corpus RAG) vs vanilla Claude/ChatGPT **without** your corpus — shows value of persistence/provenance  
- Best: report **both** briefly: (A) model choice inside your stack; (B) purpose-built corpus vs general chat  

Use the **same ~30 questions**; report RAGAS + citation metrics + qualitative notes side by side.

**6. Eval report**  
Short document: tables, top failure modes (bad retrieval vs hallucination vs weak citations), recommendation for the demo model.

### Deliverables

- `eval/questions.json` (~30)  
- Runner + results CSV  
- RAGAS summary  
- 2-model (or system-vs-ChatGPT) comparison section  
- 2–3 page eval write-up  

### Done when

You can show Fuse: citation rate, hallucination/faithfulness, and a clear statement of when your system beats generic ChatGPT (reproducibility, sources, change tracking).

---

## End-to-end flow (how the tasks connect)

```
Kickoff (schema, sources, mocks)
        │
        ├──────────────────────────────┐
        ▼                              ▼
 Database (hash + versions)     Mocks available
        │                              │
        ▼                              │
 Collect / extract ──► store ──► classify (labels)
        │                              │
        └──────────────► Time-aware RAG (chunk/embed/filter)
                                      │
                                      ▼
                         Streamlit UI + grounded citations
                                      │
                                      ▼
                    Evaluation: 30 Qs + RAGAS + 2-model compare
```

**MVP (proposal):** reduced source list + retrieval with citations.  
**Expand if capacity:** scheduling, richer classification, weekly digest.  
**Always:** public sources only; citations with dates; versions not overwrites.

---

## Quick “done” checklist per task

| Task | One-line done |
|------|----------------|
| Kickoff | Schema + sources + stack + 15–20 mocks agreed |
| Database | Versions + hash; mocks loaded; query by date works |
| Ingestion | ≥5 allowed sources land text in DB idempotently |
| Classification | Funding/Regulation/Pilot/Research (+ status) on new/changed docs |
| Time-aware RAG | Retrieve with date + label filters; citations fields ready |
| UI | Streamlit answers with source, URL, date; refuses if empty |
| Evaluation | ~30 Qs scored; RAGAS; compare 2 models / vs ChatGPT |

---

*Use with `docs/V2G_Project_Plan_Detailed.md` and `docs/V2G_Gantt_Detailed.md` for owners, dates, and subtask timing.*
