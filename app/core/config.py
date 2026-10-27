from functools import lru_cache 
from pathlib import Path 

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    app_name: str = "Agentic RAG API"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    api_v1_prefix: str = "/api/v1"
    groq_api_key: SecretStr = Field(default=SecretStr(""))
    groq_model: str = "llama-3.3-70b-versatile"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    enable_reranker: bool = False
    documents_dir:Path = "data/documents"
    chroma_dir: Path = "storage/chroma"

    chroma_collection: str = "quality_documents"

    chunk_size: int = Field(default=900, gt=0)
    chunk_overlap: int = Field(default=150, ge=0)
    retrieval_top_k: int = Field(default=10, gt=0)
    final_top_k: int = Field(default=5, ge=0)
    max_agent_attempts: int = Field(default=3)
    database_url: str = "sqlite:///./agentic_rag.db"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    return settings
