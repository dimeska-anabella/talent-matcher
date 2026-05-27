# Talent Matcher — Hackathon Team Manual

> A hands-on guide for getting the AI-powered recruiting assistant up and running during the hackathon.

---

## Table of Contents

1. [What We Are Building](#1-what-we-are-building)
2. [How It Works](#2-how-it-works)
3. [Project Structure](#3-project-structure)
4. [Getting Started](#4-getting-started)
5. [API Reference](#5-api-reference)
6. [Example Prompt & Expected Output](#6-example-prompt--expected-output)
7. [Scoring Explained](#7-scoring-explained)
8. [Suggested Team Roles](#8-suggested-team-roles)
9. [Stretch Goals](#9-stretch-goals)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. What We Are Building

**Talent Matcher** is an AI-powered recruiting assistant that finds the best candidates for any job opening.

**Input:** A job description — either typed as free text or loaded from a predefined job file.

**Output:** The **top 3 matching candidates** from a local candidate pool, each with:
- A match score (0–1)
- The skills that triggered the match
- A plain-language explanation of why they are a good fit

### Goal

> Given a job description, surface the most relevant candidates — accurately, transparently, and fast.

The system is intentionally **local-first** (no cloud infrastructure required), has **transparent scoring**, and works **without an LLM** for explanations if you prefer pure templates. This makes it easy to demo, tweak, and explain during a hackathon.

---

## 2. How It Works

```
Job Description (text)
        │
        ▼
  Embed with LiteLLM
        │
        ▼
  Query Chroma (vector DB)   ←── Candidate profiles stored as embeddings
        │
        ▼
  Retrieve top 12 candidates (semantic similarity)
        │
        ▼
  Rerank with weighted heuristic:
    70% semantic similarity
    20% required-skill overlap
    10% location bonus
        │
        ▼
  Return top 3 with scores + explanation
```

### Data included

- **31 candidate profiles** (`data/cvs/cv_001.json` … `data/cvs/cv_031.json`) — synthetic Finnish IT/consulting personas
- **11 job postings** (`data/jobs/job_001.json` … `data/jobs/job_011.json`) — roles typical at companies like Solita

---

## 3. Project Structure

```
talent-matcher/
├── app/
│   ├── api/main.py           # FastAPI routes
│   ├── config/settings.py    # All env-driven config
│   ├── models/contracts.py   # Request & response shapes
│   └── services/
│       ├── ingest.py         # Load CVs → embed → store in Chroma
│       ├── match.py          # Query + rerank logic
│       ├── explain.py        # Template & LLM explanations
│       └── text_builder.py   # Candidate/job → searchable text
├── data/
│   ├── cvs/                  # Per-candidate JSON files (ingest source)
│   ├── jobs/                 # Per-job JSON files (match-by-id source)
│   ├── candidates.json       # Consolidated view of all candidates
│   ├── jobs.json             # Consolidated view of all jobs
│   └── schemas/              # JSON schemas for data validation
├── scripts/
│   ├── ingest_data.py        # CLI: index all candidates into Chroma
│   └── normalize_data.py     # Merge data/cvs/ + data/jobs/ → consolidated JSON
├── docs/                     # Deep-dive documentation
│   ├── 01-concepts.md        # Embeddings & vector search primer
│   ├── 02-architecture.md    # Architecture diagram
│   ├── 03-hackathon-track.md # Hour-by-hour plan
│   ├── 04-tech-options.md    # Chroma alternatives, LiteLLM notes
│   └── 05-prompting-and-evaluation.md
├── requirements.txt
├── .env.example
└── README.md
```

---

## 4. Getting Started

### Prerequisites

- Python 3.9+
- An API key from any [LiteLLM-compatible provider](https://docs.litellm.ai/docs/providers) (OpenAI, Azure, etc.)

### Step 1 — Clone and set up the environment

```bash
git clone <repo-url>
cd talent-matcher

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2 — Configure your API key

```bash
cp .env.example .env
```

Open `.env` and fill in your key:

```env
LITELLM_API_KEY=sk-...          # Required — your OpenAI (or other) API key
EMBEDDING_MODEL=openai/text-embedding-3-small
CHAT_MODEL=openai/gpt-4o-mini
USE_LLM_EXPLANATIONS=false      # Set to true to get richer explanations
```

### Step 3 — Index the candidates

> All commands must be run from the project root (`talent-matcher/`), not from inside `scripts/`.

```bash
python scripts/ingest_data.py
```

Expected output:

```
Indexed candidates: 31
```

This embeds all candidate profiles and stores them in `.chroma/` (a local folder, not committed to git).

### Step 4 — Start the server

```bash
uvicorn app.api.main:app --reload
```

The server starts at `http://127.0.0.1:8000`.

Open `http://127.0.0.1:8000/docs` in your browser for the interactive Swagger UI.

---

## 5. API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Check the server is running |
| `POST` | `/ingest` | Re-index all candidates from `data/cvs/` into Chroma |
| `POST` | `/match` | Match a free-text job description |
| `POST` | `/match/job/{job_id}` | Match using a predefined job file (e.g. `job_001`) |

---

## 6. Example Prompt & Expected Output

### Example A — Free-text job description

**Request:**

```bash
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{
    "job_text": "We are looking for a senior full-stack engineer with strong React and Node.js skills, experience deploying on AWS, and a track record of mentoring junior developers."
  }'
```

**Expected response:**

```json
{
  "top_matches": [
    {
      "candidate_id": "cv_001",
      "name": "Emma Virtanen",
      "title": "Senior Software Engineer",
      "location": "Helsinki, Finland",
      "semantic_score": 0.82,
      "skills_overlap_score": 0.57,
      "bonus_score": 1.0,
      "final_score": 0.89,
      "matched_skills": ["react", "node.js", "aws"],
      "explanation": "Strong semantic alignment and overlap on react, node.js, aws. Similarity=0.820, context bonus=1.000."
    },
    {
      "candidate_id": "cv_007",
      "name": "Mikael Korhonen",
      "title": "Full-Stack Developer",
      "location": "Tampere, Finland",
      "semantic_score": 0.74,
      "skills_overlap_score": 0.43,
      "bonus_score": 0.0,
      "final_score": 0.60,
      "matched_skills": ["react", "node.js"],
      "explanation": "Good semantic match with overlap on react, node.js. Similarity=0.740, context bonus=0.000."
    },
    {
      "candidate_id": "cv_014",
      "name": "Sofia Laine",
      "title": "Cloud Engineer",
      "location": "Helsinki, Finland",
      "semantic_score": 0.69,
      "skills_overlap_score": 0.38,
      "bonus_score": 1.0,
      "final_score": 0.67,
      "matched_skills": ["aws"],
      "explanation": "Moderate semantic match with overlap on aws. Similarity=0.690, context bonus=1.000."
    }
  ]
}
```

> Note: exact scores will vary based on your embedding model. The ranking order should be stable.

---

### Example B — Match using a predefined job

**Request:**

```bash
curl -X POST http://localhost:8000/match/job/job_002
```

This loads `data/jobs/job_002.json` (Data Engineer role) and returns the top 3 matching candidates for that role.

---

### Example C — Re-index candidates via API

```bash
curl -X POST http://localhost:8000/ingest
# → {"indexed": 31}
```

---

### Example D — Health check

```bash
curl http://localhost:8000/health
# → {"status": "ok"}
```

---

### Trying it in the Swagger UI

1. Go to `http://127.0.0.1:8000/docs`
2. Click `POST /match` → `Try it out`
3. Paste this into the request body:

```json
{
  "job_text": "Looking for a data engineer experienced in Python, SQL, Spark, and building ETL pipelines on AWS."
}
```

4. Click **Execute** and inspect the results.

---

## 7. Scoring Explained

Each candidate is scored using three components:

| Component | Weight | What it measures |
|-----------|--------|-----------------|
| Semantic similarity | **70%** | How closely the candidate's profile embedding matches the job description embedding (cosine distance) |
| Skill overlap | **20%** | Fraction of the candidate's technical skills that appear in the job description text |
| Location bonus | **10%** | `1.0` if the candidate's city appears in the job text, `0.0` otherwise |

**Final score formula:**

```
final_score = 0.7 × semantic_score + 0.2 × skill_overlap_score + 0.1 × location_bonus
```

The weights are easy to change — see `app/services/match.py`. Experimenting with different weights is a great hackathon task.

---

## 8. Suggested Team Roles

| Role | Tasks |
|------|-------|
| **Backend / API** | Tune scoring weights, add new endpoints, enable LLM explanations |
| **Data** | Add or edit candidate/job JSON files, test edge cases, validate schema |
| **Evaluation** | Run 5–10 job descriptions, check that the top 3 make sense, document quality findings |
| **Demo** | Prepare 2–3 showcase scenarios (perfect fit, edge case, cross-domain), set up Swagger or Postman |

See `docs/03-hackathon-track.md` for a suggested hour-by-hour schedule.

---

## 9. Stretch Goals

Once the base system is working, here are ways to take it further:

- **Enable LLM explanations** — set `USE_LLM_EXPLANATIONS=true` in `.env` for richer candidate summaries
- **Add a simple frontend** — a text input that calls `POST /match` and renders results as cards
- **Tune the scoring weights** — experiment to improve match quality for specific job types
- **Add filters** — e.g. filter by minimum years of experience or required language
- **Evaluation set** — build a ground-truth set of (job, expected_candidate) pairs and score precision@3
- **Add more candidates** — add new JSON files to `data/cvs/` following `data/schemas/candidate.schema.json`
- **Containerise** — add a `Dockerfile` and `docker-compose.yml` for one-command setup

---

## 10. Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'app'` | You're not in the project root — `cd talent-matcher` then retry |
| `No matches returned` | You need to run ingest first: `python scripts/ingest_data.py` |
| `Validation error: job_text too short` | Job text must be at least 10 characters |
| `data/cvs/ is empty` | The folder should have files — check your git clone is complete |
| `LLM explanation fails` | The system falls back to template explanations automatically — this is expected |
| `LITELLM_API_KEY not set` | Copy `.env.example` to `.env` and add your key |
| `.chroma/ not found` | Normal on first run — it is created automatically after ingest |
| Port 8000 already in use | Run `uvicorn app.api.main:app --reload --port 8001` instead |

---

## Quick Reference Card

```bash
# Run ALL commands from the project root (talent-matcher/)

# Setup (once)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your LITELLM_API_KEY
python scripts/ingest_data.py

# Start server
uvicorn app.api.main:app --reload

# Test it
curl http://localhost:8000/health
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"job_text": "Senior React developer with AWS experience"}'

# Docs
open http://127.0.0.1:8000/docs
```

---

*Happy hacking! For deeper context on embeddings, architecture, and evaluation, check the `docs/` folder.*
