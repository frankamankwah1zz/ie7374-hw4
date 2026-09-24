# V2G Intelligence Platform — Detailed Project Plan

**Capstone for Fuse Power Management**  
**Team:** Anahid, Sandeep, Frank, Isaac  
**Start:** September 24, 2026  
**MVP due:** ~November 12, 2026 · **Handover / presentation:** November 18, 2026

---

## 1. Project summary (expanded)

Fuse tracks **Vehicle-to-Grid (V2G)** — using EV batteries as flexible grid resources. That landscape (funding, utility pilots, tariffs, standards, research) changes weekly and is scattered across Canada, the US, and Europe.

**We are building** a purpose-built system that:

1. **Monitors** an approved list of public sources on a schedule  
2. **Stores** content with provenance: source, URL, publication date, jurisdiction, labels  
3. **Answers** plain-language questions with **citations and dates** (not one-off web search)

| Phase | What it is | Without the other phase |
|-------|------------|-------------------------|
| **Phase 1 — Ingestion** | Discover → collect → extract → classify → store | A scraper with nothing to ask |
| **Phase 2 — Retrieval** | Chunk → embed → retrieve → generate in Streamlit | A chatbot with nothing grounded |

Phases run **in parallel**: RAG starts on mock documents; collectors fill the DB over time.

### Example questions the system must answer

- What V2G funding opportunities are currently open in Canada?  
- How do V2G programs in BC and California compare?  
- What has changed in the last month?

### Stretch goal

Automated weekly digest: “What changed this week in V2G,” from newly ingested / changed documents.

### Why not just ChatGPT + search

| Property | Ad-hoc search | This system |
|----------|---------------|-------------|
| Reproducibility | Different every time | Same corpus → auditable answers |
| Provenance | Often unclear | Every claim → URL + date |
| Change detection | Impossible | Snapshots / content hashes |
| Coverage | Whatever search ranks | Same source list every run |

### Constraints (from Fuse proposal)

- Public sources only; terms must allow automated access  
- Separate project account; capped API keys; no Fuse internal systems  
- ~$500 / group for four months (LLM + storage + vector DB)  
- No model training; I/O-bound workload  
- MVP = reduced source list + retrieval with citations  

---

## 2. Success criteria

**Minimum viable outcome (must ship)**

- [ ] Pipeline covers a reduced source list (suggest **5–8** sources) and lands documents in the DB  
- [ ] Each document has: source name, URL, `published_at` (or best estimate), `fetched_at`, jurisdiction, raw/extracted text, content hash  
- [ ] Streamlit UI answers questions with **citations** (source title, URL, date)  
- [ ] System says “not in corpus” when evidence is missing (no silent hallucination)  
- [ ] Evaluation set of ~30 questions scored for answer quality + citation presence  

**Nice to have (capacity-dependent)**

- [ ] Scheduled runs (cron / GitHub Actions)  
- [ ] Classification labels on every new/changed doc  
- [ ] Time filters (“last 30 days”) and label filters in retrieval  
- [ ] Weekly digest (stretch)

---

## 3. Tech stack (Task 0 decision — recommended defaults)

| Layer | Recommendation | Notes |
|-------|----------------|-------|
| Language | Python 3.11+ | Shared by all tasks |
| Document DB | PostgreSQL **or** SQLite for MVP | Postgres preferred if cloud; SQLite OK week 1 |
| Vector store | Chroma or pgvector | Stay within ~$50 vector budget |
| Embeddings | OpenAI `text-embedding-3-small` or equivalent | Cache by content hash; never re-embed unchanged docs |
| LLM | Fuse credits + Northeastern Claude where available | Cap calls; log usage |
| Collectors | `httpx` + BeautifulSoup; Playwright only if needed | PDF: `pypdf` / `pdfplumber`; Excel: `openpyxl` |
| UI | Streamlit | Sufficient per Fuse proposal |
| Schedule | GitHub Actions cron or cheap cloud scheduler | After collectors work manually |
| Config | `sources.yaml` + `.env` for keys | Source registry is code-reviewed |

**Out of scope for MVP:** custom fine-tuning, multi-user auth, scraping paywalled journals, Fuse customer data.

---

## 4. Shared document schema (Task 0 — freeze by Sept 26)

Every record is one **document** (one URL / one file version). Labels live as **columns**, not free-text blobs.

### 4.1 Core fields

| Column | Type | Required | Purpose |
|--------|------|----------|---------|
| `id` | UUID / serial | yes | Primary key |
| `source_id` | text | yes | FK to source registry |
| `title` | text | yes | Display title |
| `url` | text | yes | Canonical URL |
| `canonical_url` | text | no | After redirects |
| `published_at` | date/timestamp | preferred | Publication / effective date |
| `fetched_at` | timestamp | yes | When we collected it |
| `jurisdiction` | text / enum | yes | e.g. `CA`, `BC`, `US-CA`, `EU`, `multi` |
| `raw_path` or `raw_bytes_ref` | text | yes | Pointer to raw HTML/PDF/Excel |
| `text` | text | yes | Extracted plain text |
| `content_hash` | text (sha256) | yes | Change detection |
| `version` | int | yes | Increments when hash changes |
| `parser` | text | yes | Which extractor produced `text` |
| `language` | text | default `en` | |
| `created_at` / `updated_at` | timestamp | yes | Audit |

### 4.2 Label columns (Task 3 fills these)

| Column | Type | Example values |
|--------|------|----------------|
| `doc_type` | enum | `funding`, `pilot`, `tariff`, `standard`, `research`, `news`, `other` |
| `v2g_relevant` | bool | true / false |
| `status` | enum | `open`, `closed`, `proposed`, `active`, `unknown` |
| `confidence` | float 0–1 | Classifier confidence |
| `classified_at` | timestamp | When labels were written |
| `classifier_model` | text | Model / prompt version |

### 4.3 Source registry (`sources.yaml`)

```yaml
- id: ieso
  name: IESO
  base_url: https://www.ieso.ca
  jurisdiction: ON
  allowed_to_fetch: true   # terms/robots reviewed
  type: utility
  notes: "Check robots.txt and ToS before enabling"
```

No collector runs against a source with `allowed_to_fetch: false`.

### 4.4 Mock documents (Task 0 deliverable)

Create **15–20** mock files (mix of short HTML snippets, 1–2 PDF-like text files, and one Excel-like CSV) covering:

- Canada / BC / California funding or pilots  
- One standard (e.g. ISO 15118 mention)  
- One “closed / expired” program  
- One deliberately off-topic doc (`v2g_relevant=false`)

These unblock Tasks 4–5 before real collectors finish.

---

## 5. Task plan (elaborated)

### Task 0 — Kickoff  
**Owners:** All · **Duration:** 3 days · **Due:** Sept 26, 2026  
**Depends on:** none · **Parallel with:** none

**Do**

1. Agree schema (§4) and write it in the repo (`docs/schema.md` or SQL migration).  
2. Freeze **v1 source list** (5–8 sources; Canada + BC + California + one standards body).  
3. Choose stack (§3) and create shared repo layout.  
4. Create 15–20 mock documents + a seed script that loads them into the DB.  
5. Agree branching, PR norms, weekly Fuse check-in agenda.

**Deliverables**

- Written schema + enum definitions  
- `sources.yaml` v1 with ToS notes  
- `mocks/` folder + load script  
- One-pager: “Definition of done for MVP”

**Done when:** Frank/Isaac can create tables; Anahid/Sandeep know which URLs to fetch; Sandeep/Frank can build RAG/UI on mocks.

---

### Task 1 — Database and storage  
**Owners:** Frank, Isaac · **Duration:** 1 week · **Due:** Oct 1  
**Depends on:** Task 0 · **Parallel with:** Task 2

**Do**

1. Implement schema (tables: `sources`, `documents`, optional `document_versions` or version column).  
2. Content hash on extracted text (or raw bytes — **decide in Task 0**; recommend hash of normalized extracted text + URL).  
3. Upsert logic: same URL + same hash → no-op; same URL + new hash → new version, keep history.  
4. Simple repository API used by collectors and by RAG: `upsert_document(...)`, `list_documents(filters)`, `get_document(id)`.  
5. Backup / export path (dump to JSONL) for evaluation snapshots.

**Deliverables**

- Migrations / `schema.sql`  
- Python data-access module  
- Unit tests for hash / versioning  
- Seeded DB with mocks

**Done when:** Collectors can insert a document; RAG can read by id; “what changed since DATE” is queryable via `fetched_at` / `version`.

**Risks:** Date parsing inconsistencies → store both `published_at` and `published_at_raw`.

---

### Task 2 — Discovery, collection, extraction  
**Owners:** Anahid, Sandeep · **Duration:** 2 weeks · **Due:** Oct 8  
**Depends on:** Task 0 (source list); Task 1 to persist · **Parallel with:** Task 1 (interface on mocks first)

**Do**

1. **Source registry** wired to collectors.  
2. **Collectors** per source type: HTML list/detail pages, direct PDF, Excel/CSV.  
3. **Terms / robots check** logged in `sources.yaml` or `docs/source_access.md`.  
4. **Extraction:** HTML → main text; PDF → text; Excel → normalized tables → text.  
5. Save raw artifact + extracted text + metadata to DB via Task 1 API.  
6. Manual CLI: `python -m ingest run --source ieso` before automation.  
7. Optional later: schedule (cron) once stable.

**Suggested first sources (adjust with Fuse list)**

| Priority | Source class | Example |
|----------|--------------|---------|
| P0 | Canadian utility / ISO | IESO, BC Hydro public pages |
| P0 | Federal / provincial program pages | NRCan, provincial EV/grid pages |
| P0 | California comparator | CEC / grants portal VGI solicitations |
| P1 | Standards summary pages | Public summaries of ISO 15118 / SAE (not paywalled full standards) |
| P1 | Open research | arXiv / OA MDPI (optional; already have literature corpus) |

**Deliverables**

- Working collectors for ≥3 sources by mid-task; ≥5 by due date  
- Extraction tests on Fuse sample PDF/Excel if provided  
- Run log (success / skip / error per URL)

**Done when:** Re-running ingest is idempotent; new pages appear as new rows; changed pages bump `version`.

**Risks:** Sites that block bots → skip or use permitted RSS/API only; never fight CAPTCHAs.

---

### Task 3 — Classification at storage  
**Owner:** Isaac · **Duration:** 1–2 weeks · **Due:** Oct 15  
**Depends on:** Task 1; real text from Task 2 · **Parallel with:** Tasks 4, 5

**Do**

1. Prompt (or small classifier) that, given `title` + truncated `text`, outputs: `doc_type`, `jurisdiction`, `v2g_relevant`, `status`, `confidence`.  
2. Run **only** on new or changed documents (hash / version trigger).  
3. Persist labels as columns; store model name + prompt version.  
4. Human spot-check list (10 docs) to calibrate prompt.  
5. Fail soft: low confidence → `status=unknown` / flag for review, still retrievable.

**Deliverables**

- `classify_document(doc) -> labels`  
- Batch job for backfill  
- Confusion notes from spot-check  

**Done when:** ≥80% of sample docs have sensible `doc_type` + `jurisdiction` on spot-check; labels filterable in SQL.

**Cost control:** Cap tokens; classify title+first N chars first; full text only if needed.

---

### Task 4 — Time-aware RAG  
**Owner:** Sandeep · **Duration:** 2 weeks · **Due:** Oct 22  
**Depends on:** Task 1; mocks first, then Task 3 labels · **Parallel with:** Tasks 3, 5

**Do**

1. **Chunking:** ~512–1024 tokens, overlap; attach metadata to every chunk: `doc_id`, `url`, `title`, `published_at`, `jurisdiction`, `doc_type`, `version`.  
2. **Embeddings** + vector store; **skip re-embed** if `content_hash` unchanged.  
3. **Retrieval:** top-k vector search + optional metadata filters (jurisdiction, date range, doc_type).  
4. Prefer hybrid (keyword + vector) if time; vector-only OK for MVP.  
5. Return chunks with citation fields ready for the UI prompt.  
6. Rebuild index command after bulk ingest.

**Deliverables**

- `index_documents()` / `retrieve(query, filters) -> chunks`  
- Config for chunk size / top-k  
- Smoke test: 5 mock questions retrieve expected docs  

**Done when:** For “funding in Canada,” retrieved chunks include Canada funding mocks/docs, not only California; dates available for citation.

**Design rule:** Retrieval must support “as of / since DATE” using `published_at` or `fetched_at` filters — this is what makes the system **time-aware**.

---

### Task 5 — UI and answer prompt  
**Owner:** Frank · **Duration:** 2 weeks · **Due:** Nov 5  
**Depends on:** Starts on mocks; final path needs Task 4 · **Parallel with:** Tasks 3, 4, 6

**Do**

1. Streamlit app: question box, filters (jurisdiction, date range), answer panel, citations panel.  
2. **Answer prompt** rules:  
   - Use only retrieved chunks  
   - Cite source title, URL, date for each claim  
   - If insufficient evidence → say so  
   - Prefer newer docs when conflicts exist; mention the conflict  
3. Show “corpus as of {max fetched_at}” in the UI.  
4. Basic logging of Q&A for evaluation (Task 6).  
5. Wire to Task 4 API; keep a mock-retrieval stub for early UI work.

**Deliverables**

- `app.py` (or `ui/`) runnable locally  
- Prompt template versioned in repo  
- Screenshot for Fuse check-in  

**Done when:** A teammate can ask the three example questions and see citations; empty retrieval → explicit refusal.

---

### Task 6 — Evaluation  
**Owner:** Anahid · **Duration:** 3 weeks · **Due:** Nov 12  
**Depends on:** Questions from ~Oct 8; full runs need Tasks 4–5 · **Parallel with:** Task 5

**Do**

1. Build **~30 test questions** (gold set), tagged by type:  

   | Bucket | Count (approx.) | Purpose |
   |--------|-----------------|--------|
   | Single-doc factual | 10 | Funding + citation |
   | Jurisdiction compare (e.g. BC vs CA) | 5 | Multi-hop |
   | Temporal (“last month / open now”) | 5 | Time filters |
   | Not in corpus | 5 | Must refuse |
   | Funding / status | 5 | Label + status sensitivity |

2. For each question: expected doc ids / must-cite URLs (where applicable), acceptable answer notes.  
3. Metrics:  
   - **Answer accuracy** (human 0/1/partial)  
   - **Citation present** and **citation correct** (URL supports the claim)  
   - Optional: **RAGAs** faithfulness / answer relevance / context relevance (Es et al., 2024) as automated scorecard  
4. Compare **2 models** (e.g. Claude vs GPT, or two prompt variants) on the same retrieval.  
5. Write short eval report (tables + failure modes).

**Deliverables**

- `eval/questions.json`  
- Runner script + results CSV  
- 2–3 page eval summary  

**Done when:** Report shows citation rate and main failure modes; team knows what to fix before presentation.

**Note:** RAGAs faithfulness ≠ citation correctness. Add a manual or scripted check that cited URLs appear in retrieved chunks and dates are not invented.

---

### Task 7 — Documentation and presentation  
**Owners:** All · **Duration:** 1 week · **Due:** Nov 18  
**Depends on:** Tasks 1–6

**Do**

1. Handover docs: how to add a source, run ingest, rebuild index, start UI, set env vars, cost caps.  
2. Limitations (coverage, ToS, classification errors, eval gaps).  
3. Architecture diagram (pipeline + RAG).  
4. Demo script (3 questions live).  
5. Presentation deck + speaker notes; literature-review chapter if required by course separately.

**Deliverables**

- `README.md` (runbook)  
- Deck + demo checklist  
- Final eval + known issues  

**Done when:** A Fuse engineer can clone, configure keys, and run ingest + UI from the README alone.

---

### Stretch — Weekly digest  
**Owner:** Whoever has capacity · **~1 week if time**  
**Depends on:** Change detection (Task 1), UI or email path (Task 5)

**Do**

1. Query docs with `fetched_at` in last 7 days OR `version` bumped.  
2. Group by `doc_type` / jurisdiction.  
3. LLM summary with links + dates; refuse to invent.  
4. Output: markdown file or Streamlit “This week” page (email optional).

**Done when:** One end-to-end digest generated from real ingest diffs.

---

## 6. Timeline (Gantt-style)

```
         Sep24  Oct1   Oct8   Oct15  Oct22  Nov5   Nov12  Nov18
Task 0   ██
Task 1       ████
Task 2       ████████
Task 3             ████████
Task 4             ████████████
Task 5                   ████████████
Task 6             ░░░░░░████████████████
Task 7                                     ████
Stretch                                          ░░
```

`░` = can start early (questions / prep) · `█` = main execution

---

## 7. Who does what (RACI-style)

| Area | Frank | Isaac | Sandeep | Anahid |
|------|-------|-------|---------|--------|
| Schema / DB | **A/R** | **R** | C | C |
| Collectors / extract | C | C | **R** | **A/R** |
| Classification | C | **A/R** | C | C |
| RAG / vectors | C | C | **A/R** | C |
| Streamlit + answer prompt | **A/R** | C | C | C |
| Evaluation | C | C | C | **A/R** |
| Docs / presentation | **R** | **R** | **R** | **R** |

R = responsible · A = accountable · C = consulted

---

## 8. Repo layout (suggested)

```
/
  README.md
  docs/
    V2G_Project_Plan_Detailed.md   # this file
    schema.md
    source_access.md
  sources.yaml
  mocks/
  src/
    db/
    ingest/
    classify/
    rag/
    ui/
  eval/
    questions.json
  literature/                      # optional OA corpus already in repo
```

---

## 9. Weekly rhythm

| When | What |
|------|------|
| Weekly Fuse check-in | Show one artifact: new source landed **or** one cited answer **or** eval metric |
| Mid-week team sync (30 min) | Blockers only; update this plan’s checkboxes |
| Before each due date | PR merged to main; demoable state preferred over perfect code |

---

## 10. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Source blocks scraping | Terms check first; RSS/API; shrink source list |
| API budget overrun | Hash cache embeddings; classify truncated text; log $ |
| Dates missing on pages | `published_at` nullable + show `fetched_at` in citations |
| Hallucinated citations | Prompt rules + eval citation checks + RAGAs faithfulness |
| Task 2 slips | RAG/UI stay on mocks; MVP = 3 sources |
| Scope creep (digest, many sources) | Protect MVP; stretch only after Nov 5 demo works |

---

## 11. Definition of done (MVP checklist)

- [ ] ≥5 approved sources in registry with access notes  
- [ ] Ingest run produces documents with hash + dates + jurisdiction  
- [ ] Streamlit answers with visible citations (title, URL, date)  
- [ ] “Not in corpus” behavior verified on ≥5 eval questions  
- [ ] Eval report for ~30 questions + 2-model comparison  
- [ ] README runbook + limitations  
- [ ] Live demo of the three Fuse example questions  

---

## 12. Immediate next actions (this week — by Sept 26)

1. **All:** 60-minute kickoff — lock schema enums and stack.  
2. **Anahid / Sandeep:** Draft `sources.yaml` v1 (5–8 sources) + ToS notes.  
3. **Frank / Isaac:** Create DB migration from schema table in §4.  
4. **All:** Each person adds 4–5 mock documents (target 15–20).  
5. **Sandeep:** Stub `retrieve()` returning mock chunks for Frank’s UI.  
6. **Anahid:** Start a spreadsheet of eval questions (can be empty answers until Oct 8).  
7. Ask Fuse for: official source list + sample PDF/Excel + API credit access.

---

*Elaborated from: V2G Intelligence Platform Project Plan (team draft, start Sept 24, 2026). Aligns with Fuse Power Management capstone proposal (Sarvin Shahir, Aug 2026).*
