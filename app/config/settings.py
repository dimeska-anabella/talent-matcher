from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    litellm_api_key: Optional[str] = None
    litellm_base_url: Optional[str] = None

    embedding_model: str = "openai/text-embedding-3-small"
    chat_model: str = "openai/gpt-4o-mini"

    cvs_dir: str = "./cvs"
    jobs_dir: str = "./jobs"
    chroma_dir: str = "./.chroma"
    chroma_collection: str = "candidates"

    top_k: int = 12
    top_n: int = 3
    use_llm_explanations: bool = False

    def cvs_path(self) -> Path:
        return Path(self.cvs_dir)

    def jobs_path(self) -> Path:
        return Path(self.jobs_dir)

    def chroma_path(self) -> Path:
        return Path(self.chroma_dir)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
