import json
from pathlib import Path
from typing import Any, Dict, List


def _read_json_files(directory: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            records.append(json.load(f))
    return records


def main() -> None:
    base = Path(".")
    cvs_dir = base / "cvs"
    jobs_dir = base / "jobs"
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    candidates = _read_json_files(cvs_dir)
    jobs = _read_json_files(jobs_dir)

    candidates_path = data_dir / "candidates.json"
    jobs_path = data_dir / "jobs.json"

    with candidates_path.open("w", encoding="utf-8") as f:
        json.dump({"candidates": candidates}, f, ensure_ascii=False, indent=2)

    with jobs_path.open("w", encoding="utf-8") as f:
        json.dump({"jobs": jobs}, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(candidates)} candidates -> {candidates_path}")
    print(f"Wrote {len(jobs)} jobs -> {jobs_path}")


if __name__ == "__main__":
    main()
