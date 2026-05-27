from typing import Any, Dict, List

from litellm import completion

from app.config.settings import Settings


def template_explanation(matched_skills: List[str], semantic_score: float, bonus_score: float) -> str:
    """Return a plain-text explanation of why a candidate matched.

    Stage 4 TODO: Replace the stub return with something useful.
    You have access to matched_skills, semantic_score, and bonus_score.
    Example: mention the top matched skills and what the score means.
    """
    # TODO Stage 4: Write a meaningful explanation string.
    return "Match found."  # replace this


def llm_explanation(
    settings: Settings,
    job_text: str,
    candidate: Dict[str, Any],
    matched_skills: List[str],
    semantic_score: float,
    bonus_score: float,
) -> str:
    """Call the LLM to generate a human-readable explanation.

    Stage 4 / Bonus B TODO: Build a prompt that gives the LLM enough context
    to write a specific, useful explanation.
    Try including: candidate summary, years of experience, matched skills.
    Experiment with the temperature value — lower = more consistent, higher = more varied.
    """
    # TODO Bonus B: Build your prompt here.
    # prompt = (
    #     "You are helping explain a talent matching result.\n"
    #     "Write 1-2 concise sentences, plain language, no hype.\n\n"
    #     f"Job text:\n{job_text}\n\n"
    #     f"Candidate name: {candidate.get('name', '')}\n"
    #     f"Candidate title: {candidate.get('title', '')}\n"
    #     f"Matched skills: {', '.join(matched_skills)}\n"
    #     f"Semantic score: {semantic_score:.3f}\n"
    #     # Add more context here — candidate summary, experience, etc.
    # )

    kwargs: Dict[str, Any] = {
        "model": settings.chat_model,
        "messages": [{"role": "user", "content": ""}],  # replace "" with your prompt
        "temperature": 0.2,  # try adjusting this
    }
    if settings.litellm_api_key:
        kwargs["api_key"] = settings.litellm_api_key
    if settings.litellm_base_url:
        kwargs["api_base"] = settings.litellm_base_url
        kwargs["custom_llm_provider"] = "openai"

    try:
        response = completion(**kwargs)
        content = response.choices[0].message.content
        return content.strip() if content else template_explanation(matched_skills, semantic_score, bonus_score)
    except Exception:
        return template_explanation(matched_skills, semantic_score, bonus_score)
