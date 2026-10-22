from __future__ import annotations

import time
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Query
from app.db.session import get_db_session
from app.schemas.query import QueryMetadata, QueryRequest, QueryResponse, QuerySource
from app.services.generation.service import RAGGenerationService
from app.services.observability.metrics import record_rag_query_metrics
from app.services.retrieval.retriever import get_retriever

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_knowledge_base(
    request: QueryRequest,
    db: Annotated[Session, Depends(get_db_session)],
) -> QueryResponse:
    total_started_at = time.perf_counter()

    retrieval_strategy = request.strategy or settings.retrieval_strategy
    reranker_enabled = (
        request.rerank if request.rerank is not None else settings.reranker_enabled
    )
    retriever = get_retriever(
        retrieval_strategy,
        reranker_enabled=reranker_enabled,
    )

    retrieval_started_at = time.perf_counter()
    retrieved_chunks = retriever.search(
        query=request.query,
        top_k=request.top_k,
    )
    retrieval_latency_seconds = time.perf_counter() - retrieval_started_at
    generation_contexts = retrieved_chunks[: settings.rag_max_contexts]
    reranker_applied = any(
        chunk.reranker_score is not None for chunk in generation_contexts
    )
    reranker_latency_ms = next(
        (
            chunk.reranker_latency_ms
            for chunk in generation_contexts
            if chunk.reranker_latency_ms is not None
        ),
        None,
    )

    generation_service = RAGGenerationService()

    generation_started_at = time.perf_counter()
    generation_result = generation_service.generate(
        query=request.query,
        contexts=generation_contexts,
    )
    generation_latency_seconds = time.perf_counter() - generation_started_at

    total_latency_seconds = time.perf_counter() - total_started_at
    latency_ms = int(total_latency_seconds * 1000)

    no_answer = not generation_result.is_answerable

    sources = [
        QuerySource(
            citation_id=citation_id,
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            title=chunk.title,
            content=chunk.content,
            score=chunk.score,
            source_type=chunk.source_type,
            local_path=chunk.local_path,
            language=chunk.language,
            section_title=chunk.section_title,
            metadata=chunk.metadata,
            retrieval_strategy=chunk.retrieval_strategy,
            dense_score=chunk.dense_score,
            lexical_score=chunk.lexical_score,
            fusion_score=chunk.fusion_score,
            dense_rank=chunk.dense_rank,
            lexical_rank=chunk.lexical_rank,
            reranker_score=chunk.reranker_score,
            pre_rerank_rank=chunk.pre_rerank_rank,
            reranker_rank=chunk.reranker_rank,
            reranker_latency_ms=chunk.reranker_latency_ms,
        )
        for citation_id, chunk in enumerate(generation_contexts, start=1)
    ]

    db_query = Query(
        question=request.query,
        answer=generation_result.answer,
        language=None,
        retrieval_strategy=retrieval_strategy,
        llm_provider=generation_result.provider_name,
        latency_ms=latency_ms,
    )

    db.add(db_query)
    db.commit()

    record_rag_query_metrics(
        provider=generation_result.provider_name,
        status="success",
        total_latency_seconds=total_latency_seconds,
        retrieval_latency_seconds=retrieval_latency_seconds,
        generation_latency_seconds=generation_latency_seconds,
        retrieved_chunks_count=len(generation_contexts),
        no_answer=no_answer,
        fallback_used=generation_result.fallback_used,
        fallback_from_provider=settings.llm_provider,
        fallback_to_provider=generation_result.provider_name,
        retrieval_strategy=retrieval_strategy,
        reranker_enabled=reranker_enabled,
        reranker_applied=reranker_applied,
        reranker_model=(settings.reranker_model_name if reranker_enabled else None),
        reranker_latency_seconds=(reranker_latency_ms or 0.0) / 1000,
    )

    return QueryResponse(
        query=request.query,
        answer=generation_result.answer,
        is_answerable=generation_result.is_answerable,
        confidence=generation_result.confidence,
        sources=sources,
        metadata=QueryMetadata(
            llm_provider=generation_result.provider_name,
            retrieval_strategy=retrieval_strategy,
            latency_ms=latency_ms,
            fallback_used=generation_result.fallback_used,
            fallback_reason=generation_result.fallback_reason,
            rejection_reason=generation_result.rejection_reason,
            cited_source_ids=generation_result.cited_source_ids,
            reranker_enabled=reranker_enabled,
            reranker_applied=reranker_applied,
            reranker_model=(settings.reranker_model_name if reranker_enabled else None),
            reranker_latency_ms=reranker_latency_ms,
        ),
    )
