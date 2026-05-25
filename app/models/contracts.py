from typing import List

from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    job_text: str = Field(min_length=10)


class CandidateMatch(BaseModel):
    candidate_id: str
    name: str
    title: str
    location: str
    semantic_score: float
    skills_overlap_score: float
    bonus_score: float
    final_score: float
    matched_skills: List[str]
    explanation: str


class MatchResponse(BaseModel):
    top_matches: List[CandidateMatch]
