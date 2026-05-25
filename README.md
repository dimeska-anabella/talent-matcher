# Talent Matcher Hackathon Starter

Minimal starter for a 4-5 hour hackathon challenge:

- Input a job description
- Return top 3 matching candidates
- Explain why they match

This repo is intentionally simple and beginner-friendly for teams that are new to AI app development.

## What Is Included

- `FastAPI` backend with:
  - `POST /ingest` to index candidates
  - `POST /match` to match pasted job text
  - `POST /match/job/{job_id}` to match predefined jobs
  - `GET /health` health check
- `Chroma` vector database (local persistent folder)
- `LiteLLM`-compatible embedding/chat calls (BYOK via `.env`)
- Optional template-only explanation fallback (no LLM call required)
- Hackathon docs and architecture guidance in `docs/`

## Quick Start

1. Clone and enter repo

```bash
git clone https://github.com/dimeska-anabella/talent-matcher.git
cd talent-matcher
```

2. Create virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment

```bash
cp .env.example .env
```

Fill in:

- `LITELLM_API_KEY`
- optionally adjust `EMBEDDING_MODEL` and `CHAT_MODEL`

4. Ingest candidate data into Chroma

```bash
python scripts/ingest_data.py
```

Optional: create single-file consolidated datasets:

```bash
python scripts/normalize_data.py
```

5. Run API

```bash
uvicorn app.api.main:app --reload
```

6. Test matching

```bash
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"job_text":"Need a senior full-stack engineer with React, Node.js, AWS and mentoring experience"}'
```

## Data Layout

Current source data is in:

- `cvs/` detailed candidate profiles
- `jobs/` detailed job descriptions

Optional consolidated outputs (generated):

- `data/candidates.json`
- `data/jobs.json`

Summary files:

- `cvs.json`
- `jobs.json`

Optional schema references are in `data/schemas/`.

## Core Matching Flow

1. Flatten candidate profile JSON to searchable text.
2. Generate embeddings and store vectors in Chroma.
3. Embed incoming job text and retrieve top-K candidates.
4. Rerank with simple weighted score:
   - semantic similarity: 70%
   - required skill overlap: 20%
   - location/language bonus: 10%
5. Return top 3 with score + matched skills + short explanation.

## Project Structure

```text
app/
  api/main.py
  config/settings.py
  models/contracts.py
  services/
    ingest.py
    match.py
    explain.py
    text_builder.py
scripts/
  ingest_data.py
docs/
  01-concepts.md
  02-architecture.md
  03-hackathon-track.md
  04-tech-options.md
  05-prompting-and-evaluation.md
data/
  schemas/
    candidate.schema.json
    job.schema.json
```

## Environment Variables

See `.env.example` for all values.

Minimum required for hosted model usage:

- `LITELLM_API_KEY`
- `EMBEDDING_MODEL`
- `CHAT_MODEL` (optional if using template explanations)

## Notes for Hackathon Teams

- Keep it local-first. Do not overbuild infra.
- Ship baseline retrieval first, then improve ranking/explanations.
- If model API fails, keep demo alive with template explanations.
- Focus on clear output and explainability.

## Next Improvements (Optional)

- Add metadata filters (location, language, seniority).
- Add evaluation set with expected top matches.
- Add a better reranker (cross-encoder or LLM judge).
- Add lightweight UI (single page form + result cards).
