from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document

RAG_QUERY_TOTAL = Counter(
    "rag_query_total",
    "Total number of RAG query requests.",
    ["provider", "status"],
)

RAG_QUERY_LATENCY_SECONDS = Histogram(
    "rag_query_latency_seconds",
    "Total latency of RAG query endpoint in seconds.",
    buckets=(0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 30, 60, 120, 180, 300),
)

RAG_RETRIEVAL_LATENCY_SECONDS = Histogram(
    "rag_retrieval_latency_seconds",
    "Latency of retrieval step in seconds.",
    ["strategy"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 30),
)

RAG_GENERATION_LATENCY_SECONDS = Histogram(
    "rag_generation_latency_seconds",
    "Latency of generation step in seconds.",
    ["provider"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30, 60, 120, 300),
)

RAG_RERANKER_LATENCY_SECONDS = Histogram(
    "rag_reranker_latency_seconds",
    "Latency of the optional reranker step in seconds.",
    ["model"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30),
)

RAG_RERANKER_TOTAL = Counter(
    "rag_reranker_total",
    "Total number of optional reranker executions.",
    ["model", "status"],
)

RAG_RETRIEVED_CHUNKS_COUNT = Gauge(
    "rag_retrieved_chunks_count",
    "Number of chunks retrieved for the latest query.",
    ["endpoint"],
)

RAG_NO_ANSWER_TOTAL = Counter(
    "rag_no_answer_total",
    "Total number of RAG queries with no useful answer.",
    ["provider"],
)

RAG_LLM_FALLBACK_TOTAL = Counter(
    "rag_llm_fallback_total",
    "Total number of LLM provider fallbacks.",
    ["from_provider", "to_provider"],
)

INGESTION_DOCUMENTS_TOTAL = Gauge(
    "ingestion_documents_total",
    "Current number of ingested documents in PostgreSQL.",
)

INGESTION_CHUNKS_TOTAL = Gauge(
    "ingestion_chunks_total",
    "Current number of ingested chunks in PostgreSQL.",
)


def record_rag_query_metrics(
    *,
    provider: str,
    status: str,
    total_latency_seconds: float,
    retrieval_latency_seconds: float,
    generation_latency_seconds: float,
    retrieved_chunks_count: int,
    no_answer: bool,
    fallback_used: bool,
    fallback_from_provider: str | None,
    fallback_to_provider: str | None,
    retrieval_strategy: str,
    reranker_enabled: bool = False,
    reranker_applied: bool = False,
    reranker_model: str | None = None,
    reranker_latency_seconds: float = 0.0,
) -> None:
    RAG_QUERY_TOTAL.labels(
        provider=provider,
        status=status,
    ).inc()

    RAG_QUERY_LATENCY_SECONDS.observe(total_latency_seconds)

    RAG_RETRIEVAL_LATENCY_SECONDS.labels(
        strategy=retrieval_strategy,
    ).observe(retrieval_latency_seconds)

    RAG_GENERATION_LATENCY_SECONDS.labels(
        provider=provider,
    ).observe(generation_latency_seconds)

    RAG_RETRIEVED_CHUNKS_COUNT.labels(
        endpoint="query",
    ).set(retrieved_chunks_count)

    if reranker_enabled:
        model = reranker_model or "unknown"
        reranker_status = "success" if reranker_applied else "fallback"
        RAG_RERANKER_TOTAL.labels(
            model=model,
            status=reranker_status,
        ).inc()

        if reranker_applied:
            RAG_RERANKER_LATENCY_SECONDS.labels(
                model=model,
            ).observe(reranker_latency_seconds)

    if no_answer:
        RAG_NO_ANSWER_TOTAL.labels(
            provider=provider,
        ).inc()

    if fallback_used:
        RAG_LLM_FALLBACK_TOTAL.labels(
            from_provider=fallback_from_provider or "unknown",
            to_provider=fallback_to_provider or provider,
        ).inc()


def update_ingestion_metrics_from_db(db: Session) -> None:
    documents_count = db.query(Document).count()
    chunks_count = db.query(Chunk).count()

    INGESTION_DOCUMENTS_TOTAL.set(documents_count)
    INGESTION_CHUNKS_TOTAL.set(chunks_count)
