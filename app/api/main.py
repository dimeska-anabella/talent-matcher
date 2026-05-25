import json
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from app.config.settings import get_settings
from app.models.contracts import MatchRequest, MatchResponse
from app.services.ingest import ingest_candidates
from app.services.match import match_job_text
from app.services.text_builder import job_to_text

app = FastAPI(title="Talent Matcher API", version="0.1.0")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest")
def ingest() -> Dict[str, int]:
    settings = get_settings()
    return ingest_candidates(settings)


@app.post("/match", response_model=MatchResponse)
def match(request: MatchRequest) -> MatchResponse:
    settings = get_settings()
    try:
        return match_job_text(settings, request.job_text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/match/job/{job_id}", response_model=MatchResponse)
def match_job_id(job_id: str) -> MatchResponse:
    settings = get_settings()
    path = Path(settings.jobs_dir) / f"{job_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"job_id not found: {job_id}")

    with path.open("r", encoding="utf-8") as f:
        job: Dict[str, Any] = json.load(f)
    return match_job_text(settings, job_to_text(job))
