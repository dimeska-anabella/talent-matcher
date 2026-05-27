# Talent Matcher

AI-powered recruiting assistant — give it a job description, get back the top 3 matching candidates with scores and explanations.

**Stack:** FastAPI · ChromaDB · LiteLLM · Python 3.9+

---

## Setup

> Run all commands from the project root.

```bash
git clone https://github.com/dimeska-anabella/talent-matcher.git
cd talent-matcher

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # add your LITELLM_API_KEY

python scripts/ingest_data.py   # → Indexed candidates: 31
uvicorn app.api.main:app --reload
```

Swagger UI: `http://127.0.0.1:8000/docs`

---

## Hackathon assignment

See **[GETTING_STARTED.md](GETTING_STARTED.md)** for the full assignment, stage-by-stage instructions, and bonus challenges.

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/ingest` | Re-index all candidates into Chroma |
| `POST` | `/match` | Match free-text job description |
| `POST` | `/match/job/{job_id}` | Match predefined job (e.g. `job_001`) |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'app'` | Run from project root, not from inside `scripts/` |
| `Collection does not exist` | Complete Stage 2 in `ingest.py`, then run `python scripts/ingest_data.py` |
| `401 invalid_api_key` | Check `LITELLM_API_KEY` in `.env` |
| All scores are `0.0` | You need `"hnsw:space": "cosine"` in the collection — see Stage 2 |
| Port 8000 in use | Add `--port 8001` to the uvicorn command |
