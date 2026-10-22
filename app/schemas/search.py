from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    strategy: Literal["dense", "hybrid"] | None = None
    rerank: bool | None = None


class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int | None = None
    title: str | None = None
    content: str
    score: float
    source_type: str | None = None
    local_path: str | None = None
    language: str | None = None
    section_title: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    retrieval_strategy: Literal["dense", "hybrid"] = "dense"
    dense_score: float | None = None
    lexical_score: float | None = None
    fusion_score: float | None = None
    dense_rank: int | None = None
    lexical_rank: int | None = None
    reranker_score: float | None = None
    pre_rerank_rank: int | None = None
    reranker_rank: int | None = None
    reranker_latency_ms: float | None = None


class SearchResponse(BaseModel):
    query: str
    top_k: int
    strategy: Literal["dense", "hybrid"]
    reranker_enabled: bool
    reranker_applied: bool
    reranker_model: str | None = None
    results: list[SearchResult]
