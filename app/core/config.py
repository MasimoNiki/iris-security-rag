from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="IRIS Security RAG", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    database_url: str = Field(
        default="postgresql+psycopg://iris:iris@127.0.0.1:5433/iris",
        alias="DATABASE_URL",
    )

    qdrant_url: str = Field(
        default="http://localhost:6333",
        alias="QDRANT_URL",
    )

    qdrant_collection_name: str = Field(
        default="iris_chunks",
        alias="QDRANT_COLLECTION_NAME",
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL",
    )

    embedding_model_name: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        alias="EMBEDDING_MODEL_NAME",
    )

    chunk_size: int = Field(default=800, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, alias="CHUNK_OVERLAP")

    llm_provider: str = Field(default="extractive", alias="LLM_PROVIDER")
    llm_fallback_provider: str = Field(
        default="extractive",
        alias="LLM_FALLBACK_PROVIDER",
    )
    llm_timeout_seconds: int = Field(default=30, alias="LLM_TIMEOUT_SECONDS")
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")

    rag_min_retrieval_score: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        alias="RAG_MIN_RETRIEVAL_SCORE",
    )
    rag_max_contexts: int = Field(
        default=5,
        ge=1,
        le=20,
        alias="RAG_MAX_CONTEXTS",
    )

    retrieval_strategy: Literal["dense", "hybrid"] = Field(
        default="hybrid",
        alias="RETRIEVAL_STRATEGY",
    )
    hybrid_dense_weight: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        alias="HYBRID_DENSE_WEIGHT",
    )
    hybrid_lexical_weight: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        alias="HYBRID_LEXICAL_WEIGHT",
    )
    hybrid_rrf_k: int = Field(
        default=60,
        ge=1,
        alias="HYBRID_RRF_K",
    )
    hybrid_candidate_pool_size: int = Field(
        default=50,
        ge=5,
        le=500,
        alias="HYBRID_CANDIDATE_POOL_SIZE",
    )
    bm25_k1: float = Field(default=1.5, gt=0.0, alias="BM25_K1")
    bm25_b: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        alias="BM25_B",
    )

    reranker_enabled: bool = Field(default=False, alias="RERANKER_ENABLED")
    reranker_model_name: str = Field(
        default="cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
        alias="RERANKER_MODEL_NAME",
    )
    reranker_candidate_pool_size: int = Field(
        default=20,
        ge=5,
        le=100,
        alias="RERANKER_CANDIDATE_POOL_SIZE",
    )
    reranker_batch_size: int = Field(
        default=4,
        ge=1,
        le=64,
        alias="RERANKER_BATCH_SIZE",
    )
    reranker_max_length: int = Field(
        default=512,
        ge=128,
        le=1024,
        alias="RERANKER_MAX_LENGTH",
    )
    reranker_fail_open: bool = Field(
        default=True,
        alias="RERANKER_FAIL_OPEN",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
    )
    ollama_model: str = Field(default="qwen3:4b", alias="OLLAMA_MODEL")
    ollama_timeout_seconds: int = Field(
        default=180,
        ge=1,
        alias="OLLAMA_TIMEOUT_SECONDS",
    )
    ollama_num_ctx: int = Field(
        default=4096,
        ge=1024,
        alias="OLLAMA_NUM_CTX",
    )
    ollama_num_predict: int = Field(
        default=512,
        ge=64,
        alias="OLLAMA_NUM_PREDICT",
    )
    ollama_keep_alive: str = Field(default="5m", alias="OLLAMA_KEEP_ALIVE")

    openai_compatible_base_url: str | None = Field(
        default=None,
        alias="OPENAI_COMPATIBLE_BASE_URL",
    )
    openai_compatible_api_key: str | None = Field(
        default=None,
        alias="OPENAI_COMPATIBLE_API_KEY",
    )
    openai_compatible_model: str | None = Field(
        default=None,
        alias="OPENAI_COMPATIBLE_MODEL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
