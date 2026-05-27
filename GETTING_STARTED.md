# Talent Matcher — Hackathon Assignment

## The Challenge

You have **51 candidate profiles** (31 based in Finland, 20 in Sweden) and **11 job postings**. Build a system that takes a job description and returns the **top 3 best-matching candidates** with a score and explanation.

Complete **4 progressive stages**, each in a single file.

```
Job description → Embed → Query Chroma → Rerank (semantic + skills + location) → Top 3 + explanation
```

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your LITELLM_API_KEY
uvicorn app.api.main:app --reload
```

Swagger UI: `http://127.0.0.1:8000/docs`

---

## Team Roles

| Role | Files |
|------|-------|
| Data | `app/services/text_builder.py`, `data/cvs/`, `data/jobs/` |
| Backend | `app/services/ingest.py`, `app/services/match.py` |
| AI / Explanations | `app/services/explain.py` |
| Demo | All — own the test scenarios and final presentation |

---

## Stage 1 — Candidate document (`text_builder.py`)

**Function:** `candidate_to_text()`

Only `id`, `name`, `location`, and `summary` are active — the rest are commented out. Uncomment the fields you think are most useful for matching. There's no single right answer.

```bash
python scripts/ingest_data.py
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"job_text": "Senior React and Node.js developer with AWS experience"}'
```

---

## Stage 2 — Store in Chroma (`ingest.py`)

**Function:** `ingest_candidates()`

Uncomment the two `TODO Stage 2` blocks to create the collection and save embeddings.

> The `"hnsw:space": "cosine"` setting is required — without it all scores will be `0.000`.

```bash
python scripts/ingest_data.py
# Expected: Indexed candidates: 51
```

---

## Stage 3 — Score and rank (`match.py`)

**Functions:** `_score_candidate()`, `match_job_text()`

1. In `_score_candidate()`: replace `final_score = 0.0` with the weighted formula (uncomment it).
2. In `match_job_text()`: replace the last two lines with the sort + slice (uncomment them).

```bash
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"job_text": "Data engineer with Python, Spark, SQL and AWS pipeline experience"}'
# Top result should be cv_002 (Mikko Korhonen) with score ~0.53
```

---

## Stage 4 — Explain the match (`explain.py`)

**Functions:** `template_explanation()`, `llm_explanation()`

Replace the `"Match found."` stub with a real explanation. You have `matched_skills`, `semantic_score`, and `bonus_score` available.

```
Example: "Matched on react, node.js, aws. Semantic similarity: 0.58. Location bonus: 0."
```

Optionally enable LLM explanations: set `USE_LLM_EXPLANATIONS=true` in `.env` and build the prompt in `llm_explanation()`.

---

## Bonus Challenges

### Easy

**A — Rank labels**
Add a `rank_label` field to `CandidateMatch` (`app/models/contracts.py`) with thresholds: `>= 0.7` → `"Strong match"`, `>= 0.5` → `"Good match"`, below → `"Possible match"`. Also expose `final_score` as a percentage.

**B — LLM prompt engineering**
With `USE_LLM_EXPLANATIONS=true`, enrich the prompt in `llm_explanation()` — add the candidate's `summary`, years of experience, or tweak `temperature` (0.0 = deterministic, 1.0 = varied).

**C — Filter by location or skill**
Post-filter `ranked` in `match_job_text()` by minimum matched skills or score threshold. Or use a Chroma `where` clause to filter by location before the semantic search runs. See: [Chroma filtering docs](https://docs.trychroma.com/guides#filtering-by-metadata).

**D — Build a frontend**
The API is already running — give it a UI. Create a simple search page where users can type a job description and see the top 3 candidates rendered as cards (name, score, matched skills, explanation).

Any stack works: plain HTML + `fetch()`, React, Vue, etc. Serve static files from FastAPI or run it separately on a different port. Things to show on each card: candidate name, `final_score` (as a percentage), matched skills as tags, and the explanation text.

---

### Hard

**D — Availability-aware matching**

In a consultancy setting, a perfect skill match is useless if the consultant is already staffed. Each candidate profile already has an `available_from` date (`null` = available immediately). Add a `need_by` field to the match request and use it to filter.

- Update `text_builder.py` to include availability in the candidate document
- Update `match.py` to filter out or penalise candidates who aren't free by `need_by`
- Update `app/models/contracts.py` to accept `need_by` in the request body and expose `available_from` in the response

```json
POST /match
{ "job_text": "...", "need_by": "2026-07-01" }
```

The goal: only surface candidates who are actually free when the project starts.

---

**E — Streaming explanations**

Right now the explanation is returned as a single string once fully generated. For a real product, users expect to see text appear word by word.

- In `explain.py`, add a `stream_explanation()` function that calls LiteLLM with `stream=True` and yields chunks
- Add a new endpoint `POST /match/stream` in `app/api/main.py` that returns a [`StreamingResponse`](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse) (FastAPI built-in)
- The response should first emit the top-3 candidates as JSON, then stream the explanation for each one

```bash
curl -N -X POST http://localhost:8000/match/stream \
  -H "Content-Type: application/json" \
  -d '{"job_text": "DevOps engineer with Kubernetes and Terraform"}'
```

---

**F — Multi-role project staffing**

A consultancy rarely hires one person — they staff a whole team. Add a `POST /staff` endpoint that accepts a list of roles and returns the best non-overlapping team.

```json
POST /staff
{
  "roles": [
    "Senior React developer",
    "DevOps engineer with Kubernetes",
    "Data engineer with Python and SQL"
  ]
}
```

- Match each role independently, then resolve conflicts (the same candidate can't fill two roles)
- Return a staffing plan: one candidate per role, with scores and explanations
- Greedy assignment is fine; Hungarian algorithm is a stretch goal
