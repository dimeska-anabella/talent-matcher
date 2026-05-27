# Talent Matcher — Hackathon Assignment

## The Challenge

You have a pool of **31 candidate profiles** and **11 job postings**. Your goal is to build a system that takes a job description as input and returns the **top 3 best-matching candidates**, each with a score and a plain-language explanation of why they fit.

The infrastructure is already in place: a FastAPI server, a vector database (Chroma), and an embedding model via LiteLLM. Your job is to make the pieces work together by completing **4 progressive stages**, each in a single file.

```
Job description
      │
      ▼
  Embed with LiteLLM
      │
      ▼
  Query Chroma (vector DB)  ←── candidate profiles stored as embeddings
      │
      ▼
  Retrieve top-K by semantic similarity
      │
      ▼
  Rerank: semantic score + skill overlap + location bonus
      │
      ▼
  Return top 3 with scores + explanation
```

---

## Setup

> Run all commands from the project root (`talent-matcher/`).

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then open .env and add your LITELLM_API_KEY
```

Start the server:

```bash
uvicorn app.api.main:app --reload
```

Swagger UI: `http://127.0.0.1:8000/docs`

---

## Team Roles

| Role | Files to focus on |
|------|-------------------|
| Data | `app/services/text_builder.py`, `data/cvs/`, `data/jobs/` |
| Backend | `app/services/ingest.py`, `app/services/match.py` |
| AI / Explanations | `app/services/explain.py` |
| Demo | All — own the test scenarios and final presentation |

---

## Stage 1 — What goes into a candidate document?

**File:** `app/services/text_builder.py`  
**Function:** `candidate_to_text()`

The vector search works by comparing the job description embedding against each candidate's embedding. The quality of that comparison depends entirely on what text you put into the candidate document.

Right now only `id`, `name`, `location`, and `summary` are active. The technical skills, experience, education, and languages are all commented out.

**Your task:** Uncomment the fields that you think are most useful for matching, and add them to the `fields` list. There is no single right answer — experiment.

**How to test:** Re-ingest after any change and try a few job descriptions. Does adding experience improve results? Does soft skills add noise or signal?

```bash
python scripts/ingest_data.py
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"job_text": "Senior React and Node.js developer with AWS experience"}'
```

---

## Stage 2 — Store candidates in Chroma

**File:** `app/services/ingest.py`  
**Function:** `ingest_candidates()`

The file loading and embedding calls are already done. Two things are missing: creating the Chroma collection, and actually saving the embeddings to it.

**Your task:** Uncomment the two `TODO Stage 2` blocks.

> Pay attention to the `"hnsw:space": "cosine"` hint in the comment. Without it, all similarity scores will be `0.000`. This is a known gotcha with Chroma's default distance metric.

**How to test:**

```bash
python scripts/ingest_data.py
# Expected output: Indexed candidates: 31
```

If you see `Collection does not exist` when you call `/match`, the collection wasn't created — go back to this stage.

---

## Stage 3 — Score and rank candidates

**File:** `app/services/match.py`  
**Functions:** `_score_candidate()`, `match_job_text()`

The Chroma query is already running and returning candidates. The skill overlap and location bonus are already computed. Two things are missing: combining the signals into a final score, and sorting + slicing the results.

**Your task:**

1. In `_score_candidate()`, replace `final_score = 0.0` with the weighted formula (uncomment the line above it).
2. In `match_job_text()`, replace the last two lines with the sort + slice (uncomment those lines).

**How to test:**

```bash
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"job_text": "Data engineer with Python, Spark, SQL and AWS pipeline experience"}'
```

You should see the top result is `cv_002` (Mikko Korhonen, Senior Data Engineer) with a `final_score` around `0.53`. If all scores are `0.0` or results aren't ranked, revisit this stage.

You can also match against a predefined job:

```bash
curl -X POST http://localhost:8000/match/job/job_001
```

---

## Stage 4 — Explain the match

**File:** `app/services/explain.py`  
**Functions:** `template_explanation()`, `llm_explanation()`

Right now every result returns `"Match found."`. That tells the user nothing.

**Your task:**

1. In `template_explanation()`, replace the stub return with a useful string. You have `matched_skills`, `semantic_score`, and `bonus_score` available.
2. (Optional) Enable LLM explanations by setting `USE_LLM_EXPLANATIONS=true` in `.env`, then build the prompt in `llm_explanation()` — see Bonus B below.

**Example of a good template explanation:**

```
Matched on react, node.js, aws. Semantic similarity: 0.58. Location bonus: 0.
```

**How to test:** Run any `/match` call and check the `explanation` field in the response.

---

## Bonus Challenges

Once the 4 stages are working, pick any of the following.

### Bonus A — Score as percentage + rank label

The `final_score` is a number between 0 and 1. Make it more readable:

1. Add a `rank_label` field to `CandidateMatch` in `app/models/contracts.py`
2. Populate it in `match_job_text()` based on thresholds:
   - `>= 0.7` → `"Strong match"`
   - `>= 0.5` → `"Good match"`
   - below → `"Possible match"`
3. Also express `final_score` as a percentage (e.g. `49.4%`) — add a `score_pct` field or format it in the explanation.

---

### Bonus B — LLM prompt engineering

Set `USE_LLM_EXPLANATIONS=true` in `.env`, then improve the prompt in `llm_explanation()`.

The base prompt (commented out) is intentionally minimal. Try enriching it:

- Add the candidate's `summary` from their JSON profile
- Add years of experience (look at the `experience` array in `data/cvs/cv_001.json`)
- Change the `temperature` (0.0 = deterministic, 1.0 = varied) and compare outputs

Run the same job description multiple times and compare the quality of explanations before and after each change.

---

### Bonus C — Location or skill filter

Before returning results, filter candidates who don't meet a minimum bar.

**Option 1 — Post-filter in Python** (easiest): after building the `ranked` list in `match_job_text()`, filter out candidates with fewer than N matched skills or with a `final_score` below a threshold.

**Option 2 — Chroma `where` clause** (more powerful): pass a `where` filter to `collection.query()` to restrict results to a specific location before the semantic search even runs. See: [Chroma filtering docs](https://docs.trychroma.com/guides#filtering-by-metadata).

---

### Bonus D — Tune the scoring weights

The formula `0.7 * semantic + 0.2 * overlap + 0.1 * bonus` is a guess. Run the same 3–4 job descriptions with different weight combinations and judge the results manually.

Try for example:
- `0.5 / 0.4 / 0.1` — emphasise skill overlap more
- `0.9 / 0.05 / 0.05` — trust the embeddings almost entirely

Document which combination gives the best human-judged top 3 and explain why.

---

## Available job IDs

| ID | Title | Location |
|----|-------|----------|
| `job_001` | Senior Full-Stack Developer | Helsinki |
| `job_002` | Data Engineer | Tampere |
| `job_003` | UX/UI Designer | Helsinki |
| `job_004` | DevOps Engineer | Oulu |
| `job_005` | Machine Learning Engineer | Espoo |
| `job_006` | Project Manager | Helsinki |
| `job_007` | Cybersecurity Consultant | Helsinki |
| `job_008` | Solutions Architect | Espoo |
| `job_009` | Business Analyst | Helsinki |
| `job_010` | Service Designer | Helsinki |
| `job_011` | Senior Software Engineer | Helsinki |

Use any of these with `POST /match/job/{job_id}` or write your own free-text description with `POST /match`.

---

*For deeper background on embeddings, vector search, and architecture decisions, see the `docs/` folder.*
