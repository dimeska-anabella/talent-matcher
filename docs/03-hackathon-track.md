# 4-5 Hour Hackathon Track

## Hour 0-1: Setup + Ingestion

- Install dependencies.
- Set `.env`.
- Run `python scripts/ingest_data.py`.
- Confirm `POST /ingest` works.

## Hour 1-2: Retrieval Baseline

- Implement `POST /match`.
- Return top-k semantic matches from Chroma.
- Print candidate ids and scores.

## Hour 2-3: Reranking + Top 3

- Add weighted final scoring:
  - semantic score
  - skill overlap
  - location/language bonus
- Return top 3 only.

## Hour 3-4: Explanations + API Polish

- Add explanation text for each result.
- Support template-only fallback.
- Add `POST /match/job/{job_id}`.

## Hour 4-5: Demo Prep

- Improve response format and clarity.
- Add known limitations.
- Prepare 2 demo scenarios:
  - perfect fit
  - edge case / surprising match

## Team Split Suggestion

- Data-focused:
  - profile text flattening
  - skill overlap logic
- Software-focused:
  - API routes
  - vector DB integration
- Shared:
  - explanation quality
  - demo story
