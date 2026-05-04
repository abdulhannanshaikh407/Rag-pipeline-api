"""
Application configuration management.
All settings are loaded from environment variables with type validation.
"""
from functools import lru_cache
from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────
    llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="", alias="OPENAI_BASE_URL")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=2048, ge=1, le=8192)

    # ── Embeddings ────────────────────────────────────────
    embedding_provider: Literal["openai", "huggingface"] = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # ── Vector Store ──────────────────────────────────────
    vector_store: Literal["chroma", "faiss", "pinecone"] = "chroma"
    chroma_persist_dir: str = "./data/vectorstore"
    pinecone_api_key: str = ""
    pinecone_env: str = ""
    pinecone_index_name: str = "rag-index"

    # ── Storage ───────────────────────────────────────────
    storage_backend: Literal["local", "s3"] = "local"
    local_upload_dir: str = "./data/documents"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = ""
    aws_region: str = "us-east-1"

    # ── API Security ──────────────────────────────────────
    api_key: str = "changeme"
    api_key_header: str = "X-API-Key"
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # ── Auth (JWT) ────────────────────────────────────────
    secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION", alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)

    # ── Caching ───────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600

    # ── Chunking ──────────────────────────────────────────
    chunk_size: int = Field(default=800, ge=100, le=8000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)
    chunking_strategy: Literal["recursive", "semantic"] = "recursive"

    # ── Retrieval ─────────────────────────────────────────
    retrieval_top_k: int = Field(default=5, ge=1, le=20)
    hybrid_search_enabled: bool = True
    bm25_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    vector_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    query_rewriting_enabled: bool = True

    # ── App ───────────────────────────────────────────────
    app_env: Literal["development", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["http://localhost:8501", "http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — call this everywhere."""
    return Settings()