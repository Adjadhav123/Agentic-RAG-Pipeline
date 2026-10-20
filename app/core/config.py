from pydantic.functional_validators import FieldValidatorModes
from asyncio import SelectorEventLoop
from  functools import lru_cache 
from pathlib import Path 

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    app_name: str = "Agentic ARP API"
    app_env: str = "development"
    dubug: bool = False
    log_level: str = "INFO"

    app_v1_prefix: str = "/app/v1"
    groq_api_key: SecretStr = Field(default=SecretStr("GROQ_API_KEY"))
    groq_model: str = "GROQ_MODEL"

    embedding_model: str = "EMBEDDING_MODEL"
    reranker_model: str = "RERANKER_MODEL"

    enable_reranker: bool = False
    documents_dir:Path = "data/documents"
    chroma_dir: Path = "storage/chroma"

    chroma_collection: str = "quality_documents"

    chunk_size: int = Field(default=900, gt=0)
    chunk_overlap: int = Field(default=150, ge=0)
    retrieval_top_k: int = Field(default=10, gt=0)
    final_top_k: int = Field(default=5, ge=0)
    max_agent_attempts: int = Field(default=3)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    return settings
