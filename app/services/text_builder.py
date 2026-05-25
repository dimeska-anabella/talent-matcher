from typing import Any, Dict, List


def _collect_experience(cand: Dict[str, Any]) -> str:
    entries = cand.get("experience", [])
    parts: List[str] = []
    for item in entries:
        title = item.get("title", "")
        company = item.get("company", "")
        description = item.get("description", "")
        technologies = ", ".join(item.get("technologies", []))
        responsibilities = ", ".join(item.get("responsibilities", []))
        parts.append(
            " | ".join(
                chunk
                for chunk in [title, company, description, technologies, responsibilities]
                if chunk
            )
        )
    return "\n".join(parts)


def candidate_to_text(cand: Dict[str, Any]) -> str:
    personal = cand.get("personal_info", {})
    skills = cand.get("skills", {})
    technical = ", ".join(skills.get("technical", []))
    soft = ", ".join(skills.get("soft", []))
    languages = ", ".join(f'{l.get("language", "")}:{l.get("proficiency", "")}' for l in cand.get("languages", []))
    education = ", ".join(ed.get("degree", "") for ed in cand.get("education", []))

    fields = [
        cand.get("id", ""),
        personal.get("name", ""),
        personal.get("location", ""),
        cand.get("summary", ""),
        technical,
        soft,
        _collect_experience(cand),
        education,
        languages,
    ]
    return "\n".join(value for value in fields if value)


def job_to_text(job: Dict[str, Any]) -> str:
    company = job.get("company", {})
    required = job.get("required_qualifications", {})
    preferred = job.get("preferred_qualifications", {})

    required_skills = ", ".join(required.get("skills", []))
    preferred_skills = ", ".join(preferred.get("skills", []))
    responsibilities = ", ".join(job.get("responsibilities", []))

    fields = [
        job.get("id", ""),
        job.get("title", ""),
        company.get("name", ""),
        company.get("location", ""),
        job.get("summary", ""),
        responsibilities,
        required_skills,
        preferred_skills,
    ]
    return "\n".join(value for value in fields if value)


def extract_candidate_technical_skills(cand: Dict[str, Any]) -> List[str]:
    return [skill.lower() for skill in cand.get("skills", {}).get("technical", [])]
