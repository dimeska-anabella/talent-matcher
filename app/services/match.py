import json
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from litellm import embedding

from app.config.settings import Settings
from app.models.contracts import CandidateMatch, MatchResponse
from app.services.explain import llm_explanation, template_explanation
from app.services.text_builder import extract_candidate_technical_skills


def _embed_query(settings: Settings, text: str) -> List[float]:
    kwargs: Dict[str, Any] = {
        "model": settings.embedding_model,
        "input": [text],
    }
    if settings.litellm_api_key:
        kwargs["api_key"] = settings.litellm_api_key
    if settings.litellm_base_url:
        kwargs["api_base"] = settings.litellm_base_url
        kwargs["custom_llm_provider"] = "openai"
    response = embedding(**kwargs)
    return response.data[0]["embedding"]


def _load_candidates(settings: Settings) -> Dict[str, Dict[str, Any]]:
    by_id: Dict[str, Dict[str, Any]] = {}
    for path in sorted(Path(settings.cvs_dir).glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            cand = json.load(f)
        by_id[cand.get("id", path.stem)] = cand
    return by_id


def _normalize_skill_tokens(job_text: str) -> List[str]:
    separators = [",", ".", ";", "\n", "/", "(", ")", ":"]
    normalized = job_text.lower()
    for sep in separators:
        normalized = normalized.replace(sep, " ")
    return [token.strip() for token in normalized.split(" ") if token.strip()]


def _location_bonus(job_text: str, location: str) -> float:
    if not location:
        return 0.0
    return 1.0 if location.lower().split(",")[0] in job_text.lower() else 0.0


def _score_candidate(job_text: str, semantic_score: float, candidate: Dict[str, Any]) -> Dict[str, Any]:
    job_tokens = set(_normalize_skill_tokens(job_text))
    skills = extract_candidate_technical_skills(candidate)
    skills_tokens = {item.lower() for item in skills}
    matched = sorted([s for s in skills_tokens if any(tok in s for tok in job_tokens)])

    overlap = len(matched) / max(1, len(skills_tokens))
    location = candidate.get("personal_info", {}).get("location", "")
    bonus = _location_bonus(job_text, location)

    final_score = (0.7 * semantic_score) + (0.2 * overlap) + (0.1 * bonus)
    return {
        "matched_skills": matched,
        "skills_overlap_score": overlap,
        "bonus_score": bonus,
        "final_score": final_score,
    }


def match_job_text(settings: Settings, job_text: str) -> MatchResponse:
    client = chromadb.PersistentClient(path=str(settings.chroma_path()))
    collection = client.get_collection(settings.chroma_collection)
    query_embedding = _embed_query(settings, job_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=settings.top_k,
        include=["metadatas", "distances"],
    )

    ids = results.get("ids", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    all_candidates = _load_candidates(settings)
    ranked: List[CandidateMatch] = []

    for candidate_id, metadata, distance in zip(ids, metadatas, distances):
        # Chroma distance is lower-is-better for cosine distance, invert to a similarity-like signal.
        semantic_score = max(0.0, 1.0 - float(distance))
        candidate_json = all_candidates.get(candidate_id, {})
        scoring = _score_candidate(job_text, semantic_score, candidate_json)

        candidate_summary = {
            "name": metadata.get("name", ""),
            "title": metadata.get("title", ""),
            "location": metadata.get("location", ""),
        }
        if settings.use_llm_explanations:
            explanation = llm_explanation(
                settings,
                job_text=job_text,
                candidate=candidate_summary,
                matched_skills=scoring["matched_skills"],
                semantic_score=semantic_score,
                bonus_score=scoring["bonus_score"],
            )
        else:
            explanation = template_explanation(scoring["matched_skills"], semantic_score, scoring["bonus_score"])

        ranked.append(
            CandidateMatch(
                candidate_id=candidate_id,
                name=metadata.get("name", ""),
                title=metadata.get("title", ""),
                location=metadata.get("location", ""),
                semantic_score=semantic_score,
                skills_overlap_score=scoring["skills_overlap_score"],
                bonus_score=scoring["bonus_score"],
                final_score=scoring["final_score"],
                matched_skills=scoring["matched_skills"],
                explanation=explanation,
            )
        )

    ranked.sort(key=lambda item: item.final_score, reverse=True)
    return MatchResponse(top_matches=ranked[: settings.top_n])
