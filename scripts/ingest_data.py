from app.config.settings import get_settings
from app.services.ingest import ingest_candidates


def main() -> None:
    settings = get_settings()
    result = ingest_candidates(settings)
    print(f"Indexed candidates: {result['indexed']}")


if __name__ == "__main__":
    main()
