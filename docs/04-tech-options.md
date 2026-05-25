# Tech Options

## Default Stack (Recommended)

- Backend: Python + FastAPI
- Vector DB: Chroma (local persistent mode)
- Model Gateway: LiteLLM-compatible API

This is the fastest path for teams with mixed skill levels.

## Why Chroma As Default

- Zero external infra required.
- Good developer ergonomics for local prototypes.
- Easy to replace later with managed vector DB.

## Alternatives (If Teams Want)

- Qdrant
- pgvector (Postgres extension)
- Pinecone

## Embeddings / LLM Provider Notes

- Keep provider details in `.env`.
- Use `EMBEDDING_MODEL` and `CHAT_MODEL`.
- Keep code provider-agnostic via LiteLLM interface.
