from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.search import SearchResult


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    strategy: Literal["dense", "hybrid"] | None = None
    rerank: bool | None = None


class QueryMetadata(BaseModel):
    llm_provider: str
    retrieval_strategy: str
    latency_ms: int
    fallback_used: bool = False
    fallback_reason: str | None = None
    rejection_reason: str | None = None
    cited_source_ids: list[int] = Field(default_factory=list)
    reranker_enabled: bool = False
    reranker_applied: bool = False
    reranker_model: str | None = None
    reranker_latency_ms: float | None = None


class QuerySource(SearchResult):
    citation_id: int


class QueryResponse(BaseModel):
    query: str
    answer: str
    is_answerable: bool
    confidence: float
    sources: list[QuerySource]
    metadata: QueryMetadata
