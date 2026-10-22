from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.services.retrieval.retriever import RetrievedChunk


@dataclass
class EvalQuestionResult:
    question_id: str
    question: str
    language: str
    tags: list[str]
    answerable: bool

    hit: bool
    document_hit: bool
    content_hit: bool
    reciprocal_rank: float
    document_reciprocal_rank: float
    content_reciprocal_rank: float
    first_relevant_rank: int | None
    first_document_rank: int | None
    first_content_rank: int | None
    keyword_recall: float | None

    latency_ms: int
    answer_has_sources: bool
    no_answer: bool
    answerability_correct: bool
    reranker_applied: bool = False
    reranker_latency_ms: float | None = None

    matched_keywords: list[str] = field(default_factory=list)
    expected_source_keywords: list[str] = field(default_factory=list)
    expected_external_ids: list[str] = field(default_factory=list)
    expected_local_paths: list[str] = field(default_factory=list)

    provider_name: str | None = None
    generation_confidence: float | None = None
    generated_is_answerable: bool | None = None
    rejection_reason: str | None = None
    cited_source_ids: list[int] = field(default_factory=list)
    fallback_used: bool = False
    answer: str | None = None
    top_results: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class EvalSummary:
    schema_version: int
    retrieval_strategy: str
    total_questions: int
    answerable_questions: int
    unanswerable_questions: int
    document_evaluable_questions: int
    content_evaluable_questions: int
    top_k: int
    no_answer_threshold: float
    reranker_enabled: bool
    reranker_applied_rate: float

    hit_at_k: float
    document_hit_at_k: float
    content_hit_at_k: float
    recall_at_k: float
    mrr: float
    document_mrr: float
    content_mrr: float

    average_latency_ms: float
    answer_has_sources_rate: float
    no_answer_rate: float
    answerable_no_answer_rate: float
    unanswerable_rejection_rate: float
    answerability_accuracy: float


def normalize_text(text: str | None) -> str:
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_path(path: str | None) -> str:
    return normalize_text((path or "").replace("\\", "/"))


def get_chunk_external_id(chunk: RetrievedChunk) -> str | None:
    metadata = chunk.metadata or {}
    value = metadata.get("external_id")

    if value is None:
        return None

    normalized_value = str(value).strip()

    return normalized_value or None


def build_searchable_text(chunk: RetrievedChunk) -> str:
    parts = [
        chunk.title,
        chunk.content,
        chunk.source_type,
        chunk.local_path,
        chunk.language,
        chunk.section_title,
        get_chunk_external_id(chunk),
    ]

    metadata = chunk.metadata or {}

    for value in metadata.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)

    return normalize_text(" ".join(part for part in parts if part))


def get_matched_keywords(
    chunks: list[RetrievedChunk],
    expected_keywords: list[str],
) -> list[str]:
    combined_text = normalize_text(
        " ".join(build_searchable_text(chunk) for chunk in chunks),
    )

    return [
        keyword
        for keyword in expected_keywords
        if normalize_text(keyword) in combined_text
    ]


def get_chunk_matched_keywords(
    chunk: RetrievedChunk,
    expected_keywords: list[str],
) -> list[str]:
    searchable_text = build_searchable_text(chunk)

    return [
        keyword
        for keyword in expected_keywords
        if normalize_text(keyword) in searchable_text
    ]


def chunk_matches_expected_document(
    chunk: RetrievedChunk,
    *,
    expected_external_ids: list[str],
    expected_local_paths: list[str],
) -> bool:
    normalized_external_ids = {normalize_text(value) for value in expected_external_ids}
    normalized_local_paths = {normalize_path(value) for value in expected_local_paths}
    external_id = normalize_text(get_chunk_external_id(chunk))
    local_path = normalize_path(chunk.local_path)

    return bool(
        (external_id and external_id in normalized_external_ids)
        or (local_path and local_path in normalized_local_paths),
    )


def find_first_document_rank(
    chunks: list[RetrievedChunk],
    *,
    expected_external_ids: list[str],
    expected_local_paths: list[str],
) -> int | None:
    if not (expected_external_ids or expected_local_paths):
        return None

    for index, chunk in enumerate(chunks, start=1):
        if chunk_matches_expected_document(
            chunk,
            expected_external_ids=expected_external_ids,
            expected_local_paths=expected_local_paths,
        ):
            return index

    return None


def find_first_content_rank(
    chunks: list[RetrievedChunk],
    *,
    expected_keywords: list[str],
    min_keyword_matches: int,
) -> int | None:
    if not expected_keywords:
        return None

    for index, chunk in enumerate(chunks, start=1):
        matched_keywords = get_chunk_matched_keywords(
            chunk=chunk,
            expected_keywords=expected_keywords,
        )

        if len(matched_keywords) >= min_keyword_matches:
            return index

    return None


def calculate_keyword_recall(
    matched_keywords: list[str],
    expected_keywords: list[str],
) -> float | None:
    if not expected_keywords:
        return None

    return len(set(matched_keywords)) / len(set(expected_keywords))


def _rate(values: list[bool]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def _mean(values: list[float | int]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def summarize_eval_results(
    results: list[EvalQuestionResult],
    *,
    top_k: int,
    no_answer_threshold: float,
    retrieval_strategy: str = "dense",
    reranker_enabled: bool = False,
) -> EvalSummary:
    answerable_results = [result for result in results if result.answerable]
    unanswerable_results = [result for result in results if not result.answerable]
    document_results = [
        result
        for result in answerable_results
        if result.expected_external_ids or result.expected_local_paths
    ]
    content_results = [
        result for result in answerable_results if result.expected_source_keywords
    ]
    keyword_recalls = [
        result.keyword_recall
        for result in content_results
        if result.keyword_recall is not None
    ]

    return EvalSummary(
        schema_version=2,
        retrieval_strategy=retrieval_strategy,
        total_questions=len(results),
        answerable_questions=len(answerable_results),
        unanswerable_questions=len(unanswerable_results),
        document_evaluable_questions=len(document_results),
        content_evaluable_questions=len(content_results),
        top_k=top_k,
        no_answer_threshold=no_answer_threshold,
        reranker_enabled=reranker_enabled,
        reranker_applied_rate=_rate([result.reranker_applied for result in results]),
        hit_at_k=_rate([result.hit for result in answerable_results]),
        document_hit_at_k=_rate(
            [result.document_hit for result in document_results],
        ),
        content_hit_at_k=_rate(
            [result.content_hit for result in content_results],
        ),
        recall_at_k=_mean(keyword_recalls),
        mrr=_mean(
            [result.reciprocal_rank for result in answerable_results],
        ),
        document_mrr=_mean(
            [result.document_reciprocal_rank for result in document_results],
        ),
        content_mrr=_mean(
            [result.content_reciprocal_rank for result in content_results],
        ),
        average_latency_ms=_mean(
            [result.latency_ms for result in results],
        ),
        answer_has_sources_rate=_rate(
            [result.answer_has_sources for result in answerable_results],
        ),
        no_answer_rate=_rate(
            [result.no_answer for result in results],
        ),
        answerable_no_answer_rate=_rate(
            [result.no_answer for result in answerable_results],
        ),
        unanswerable_rejection_rate=_rate(
            [result.no_answer for result in unanswerable_results],
        ),
        answerability_accuracy=_rate(
            [result.answerability_correct for result in results],
        ),
    )
