# Concepts For Beginners

## Problem

Given a job description, return the top 3 matching candidates.

## Core AI Concepts

- **Embedding**: converts text into a numeric vector that preserves meaning.
- **Vector Search**: finds text with the closest semantic meaning.
- **Reranking**: applies business rules on top of semantic similarity.
- **Explainability**: shows why a candidate is recommended.

## Practical Baseline

1. Embed each candidate profile.
2. Store vectors in Chroma.
3. Embed input job text.
4. Retrieve top K semantically similar candidates.
5. Rerank and output top 3 with reasons.

## Why This Works In A Hackathon

- Very fast to implement.
- Easy to explain during demos.
- Can be improved incrementally (better models, better scoring, better UI).
