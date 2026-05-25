import json
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from litellm import embedding

from app.config.settings import Settings
from app.services.text_builder import candidate_to_text


def _embed_text(settings: Settings, text: str) -> List[float]:
    kwargs: Dict[str, Any] = {
        "model": settings.embedding_model,
        "input": [text],
    }
    if settings.litellm_api_key:
        kwargs["api_key"] = settings.litellm_api_key
    if settings.litellm_base_url:
        kwargs["base_url"] = settings.litellm_base_url

    response = embedding(**kwargs)
    return response.data[0]["embedding"]


def _load_candidate_files(cvs_dir: Path) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for path in sorted(cvs_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            candidates.append(json.load(f))
    return candidates


def ingest_candidates(settings: Settings) -> Dict[str, int]:
    settings.chroma_path().mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(settings.chroma_path()))
    collection = client.get_or_create_collection(settings.chroma_collection)

    candidates = _load_candidate_files(settings.cvs_path())

    ids: List[str] = []
    docs: List[str] = []
    metadatas: List[Dict[str, str]] = []
    embeddings: List[List[float]] = []

    for cand in candidates:
        candidate_id = cand.get("id", "")
        personal = cand.get("personal_info", {})
        experience = cand.get("experience", [{}])
        current_title = experience[0].get("title", "") if experience else ""
        location = personal.get("location", "")
        name = personal.get("name", "")

        doc = candidate_to_text(cand)
        emb = _embed_text(settings, doc)

        ids.append(candidate_id)
        docs.append(doc)
        embeddings.append(emb)
        metadatas.append(
            {
                "name": name,
                "title": current_title,
                "location": location,
            }
        )

    if ids:
        collection.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)

    return {"indexed": len(ids)}
