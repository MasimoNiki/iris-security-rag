from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.services.evaluation.dataset import GoldenQuestion
from app.services.evaluation.metrics import (
    calculate_keyword_recall,
    find_first_content_rank,
    find_first_document_rank,
    get_matched_keywords,
)
from app.services.retrieval.retriever import get_retriever

RETRIEVAL_PROFILES = ("dense", "hybrid", "hybrid_reranked")


@dataclass
class RetrievalQuestionResult:
    question_id: str
    question: str
    strategy: str
    document_evaluable: bool
    content_evaluable: bool
    document_hit: bool
    content_hit: bool
    first_document_rank: int | None
    first_content_rank: int | None
    primary_reciprocal_rank: float
    document_reciprocal_rank: float
    content_reciprocal_rank: float
    keyword_recall: float | None
    latency_ms: float
    top_chunk_ids: list[int]
    reranker_applied: bool
    reranker_scores: list[float | None]


@dataclass
class RetrievalStrategySummary:
    strategy: str
    answerable_questions: int
    top_k: int
    document_hit_at_k: float
    content_hit_at_k: float
    keyword_recall_at_k: float
    primary_mrr: float
    document_mrr: float
    content_mrr: float
    average_latency_ms: float
    reranker_applied_rate: float


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def resolve_retrieval_profile(profile: str) -> tuple[str, bool]:
    if profile == "dense":
        return "dense", False
    if profile == "hybrid":
        return "hybrid", False
    if profile == "hybrid_reranked":
        return "hybrid", True

    raise ValueError(
        f"Unsupported retrieval profile: {profile}. "
        f"Use one of: {', '.join(RETRIEVAL_PROFILES)}."
    )


def warm_up_retrieval_profile(
    *,
    profile: str,
    query: str,
    top_k: int,
) -> float:
    strategy, reranker_enabled = resolve_retrieval_profile(profile)
    retriever = get_retriever(
        strategy,
        reranker_enabled=reranker_enabled,
    )
    started_at = time.perf_counter()
    retriever.search(query, top_k=top_k)
    return (time.perf_counter() - started_at) * 1000


def evaluate_retrieval_strategy(
    *,
    questions: list[GoldenQuestion],
    strategy: str,
    top_k: int,
) -> tuple[RetrievalStrategySummary, list[RetrievalQuestionResult]]:
    retrieval_strategy, reranker_enabled = resolve_retrieval_profile(strategy)
    retriever = get_retriever(
        retrieval_strategy,
        reranker_enabled=reranker_enabled,
    )
    results: list[RetrievalQuestionResult] = []

    for question in questions:
        if not question.answerable:
            continue

        started_at = time.perf_counter()
        chunks = retriever.search(question.question, top_k=top_k)
        latency_ms = (time.perf_counter() - started_at) * 1000

        first_document_rank = find_first_document_rank(
            chunks=chunks,
            expected_external_ids=question.expected_external_ids,
            expected_local_paths=question.expected_local_paths,
        )
        first_content_rank = find_first_content_rank(
            chunks=chunks,
            expected_keywords=question.expected_source_keywords,
            min_keyword_matches=question.min_keyword_matches,
        )
        document_hit = (
            first_document_rank is not None
            if question.has_document_expectation
            else first_content_rank is not None
        )
        content_hit = (
            first_content_rank is not None
            if question.has_content_expectation
            else document_hit
        )
        primary_rank = (
            first_document_rank
            if question.has_document_expectation
            else first_content_rank
        )
        matched_keywords = get_matched_keywords(
            chunks=chunks,
            expected_keywords=question.expected_source_keywords,
        )

        results.append(
            RetrievalQuestionResult(
                question_id=question.id,
                question=question.question,
                strategy=strategy,
                document_evaluable=question.has_document_expectation,
                content_evaluable=question.has_content_expectation,
                document_hit=document_hit,
                content_hit=content_hit,
                first_document_rank=first_document_rank,
                first_content_rank=first_content_rank,
                primary_reciprocal_rank=1 / primary_rank if primary_rank else 0.0,
                document_reciprocal_rank=(
                    1 / first_document_rank if first_document_rank else 0.0
                ),
                content_reciprocal_rank=(
                    1 / first_content_rank if first_content_rank else 0.0
                ),
                keyword_recall=calculate_keyword_recall(
                    matched_keywords=matched_keywords,
                    expected_keywords=question.expected_source_keywords,
                ),
                latency_ms=latency_ms,
                top_chunk_ids=[chunk.chunk_id for chunk in chunks],
                reranker_applied=any(
                    chunk.reranker_score is not None for chunk in chunks
                ),
                reranker_scores=[chunk.reranker_score for chunk in chunks],
            )
        )

    document_results = [result for result in results if result.document_evaluable]
    content_results = [result for result in results if result.content_evaluable]
    keyword_recalls = [
        result.keyword_recall
        for result in content_results
        if result.keyword_recall is not None
    ]
    summary = RetrievalStrategySummary(
        strategy=strategy,
        answerable_questions=len(results),
        top_k=top_k,
        document_hit_at_k=_mean(
            [float(result.document_hit) for result in document_results]
        ),
        content_hit_at_k=_mean(
            [float(result.content_hit) for result in content_results]
        ),
        keyword_recall_at_k=_mean(keyword_recalls),
        primary_mrr=_mean(
            [result.primary_reciprocal_rank for result in results],
        ),
        document_mrr=_mean(
            [result.document_reciprocal_rank for result in document_results],
        ),
        content_mrr=_mean(
            [result.content_reciprocal_rank for result in content_results],
        ),
        average_latency_ms=_mean([result.latency_ms for result in results]),
        reranker_applied_rate=_mean(
            [float(result.reranker_applied) for result in results]
        ),
    )

    return summary, results


def save_retrieval_comparison(
    *,
    output_path: Path,
    summaries: list[RetrievalStrategySummary],
    results_by_strategy: dict[str, list[RetrievalQuestionResult]],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 2,
        "generated_at": datetime.now(UTC).isoformat(),
        "summaries": [asdict(summary) for summary in summaries],
        "results": {
            strategy: [asdict(result) for result in results]
            for strategy, results in results_by_strategy.items()
        },
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
