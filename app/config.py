import os
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./storage/titleguard.db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: str = "./storage/faiss/title_index.faiss"
    FAISS_ID_MAP_PATH: str = "./storage/faiss/id_map.json"
    FAISS_METADATA_PATH: str = "./storage/faiss/index_metadata.json"
    FAISS_TOP_K: int = 20
    CLUSTER_METADATA_PATH: str = "./storage/clusters/cluster_metadata.json"
    CLUSTER_TOP_N: int = 3

    SEMANTIC_WEIGHT: float = 0.50
    LEXICAL_WEIGHT: float = 0.30
    PHONETIC_WEIGHT: float = 0.20

    SCORE_THRESHOLD_CONFLICT: float = 0.75
    SCORE_THRESHOLD_REVIEW: float = 0.50

    ADMIN_API_KEY: str = "replace-with-secure-value"
    CORS_ORIGINS: str = "http://localhost:8000,http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
