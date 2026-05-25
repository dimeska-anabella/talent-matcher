from typing import Any, Dict, List

from litellm import completion

from app.config.settings import Settings


def template_explanation(matched_skills: List[str], semantic_score: float, bonus_score: float) -> str:
    skills_fragment = ", ".join(matched_skills[:5]) if matched_skills else "relevant role experience"
    return (
        f"Strong semantic alignment and overlap on {skills_fragment}. "
        f"Similarity={semantic_score:.3f}, context bonus={bonus_score:.3f}."
    )


def llm_explanation(
    settings: Settings,
    job_text: str,
    candidate: Dict[str, Any],
    matched_skills: List[str],
    semantic_score: float,
    bonus_score: float,
) -> str:
    prompt = (
        "You are helping explain a talent matching result.\n"
        "Write 1-2 concise sentences, plain language, no hype.\n\n"
        f"Job text:\n{job_text}\n\n"
        f"Candidate name: {candidate.get('name', '')}\n"
        f"Candidate title: {candidate.get('title', '')}\n"
        f"Matched skills: {', '.join(matched_skills)}\n"
        f"Semantic score: {semantic_score:.3f}\n"
        f"Bonus score: {bonus_score:.3f}\n"
    )

    kwargs: Dict[str, Any] = {
        "model": settings.chat_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    if settings.litellm_api_key:
        kwargs["api_key"] = settings.litellm_api_key
    if settings.litellm_base_url:
        kwargs["base_url"] = settings.litellm_base_url

    try:
        response = completion(**kwargs)
        content = response.choices[0].message.content
        return content.strip() if content else template_explanation(matched_skills, semantic_score, bonus_score)
    except Exception:
        return template_explanation(matched_skills, semantic_score, bonus_score)
