from __future__ import annotations

import math
import time
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import yaml


@dataclass(frozen=True)
class BatchQuestion:
    id: str
    question: str
    expected_answerable: bool | None = None


@dataclass
class BatchResult:
    sequence: int
    iteration: int
    question_id: str
    question: str
    expected_answerable: bool | None
    status: str
    http_status: int | None
    elapsed_ms: int
    api_latency_ms: int | None = None
    is_answerable: bool | None = None
    confidence: float | None = None
    sources_count: int = 0
    cited_source_ids: list[int] | None = None
    provider: str | None = None
    retrieval_strategy: str | None = None
    reranker_enabled: bool | None = None
    reranker_applied: bool | None = None
    reranker_latency_ms: float | None = None
    fallback_used: bool | None = None
    rejection_reason: str | None = None
    answer: str | None = None
    sources: list[dict[str, Any]] | None = None
    error: str | None = None


def load_batch_questions(dataset_path: Path) -> list[BatchQuestion]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Question dataset not found: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as file:
        raw_items = yaml.safe_load(file)

    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("Question dataset must contain a non-empty YAML/JSON list.")

    questions: list[BatchQuestion] = []
    for index, item in enumerate(raw_items, start=1):
        if isinstance(item, str):
            question_text = item.strip()
            question_id = f"q{index:03d}"
            expected_answerable = None
        elif isinstance(item, dict):
            question_text = str(item.get("question", "")).strip()
            question_id = str(item.get("id") or f"q{index:03d}").strip()
            raw_answerable = item.get("answerable")
            if raw_answerable is not None and not isinstance(raw_answerable, bool):
                raise ValueError(
                    f"{question_id}: answerable must be true or false."
                )
            expected_answerable = raw_answerable
        else:
            raise ValueError(f"Dataset item #{index} must be text or a mapping.")

        if not question_text:
            raise ValueError(f"{question_id}: question must not be empty.")

        questions.append(
            BatchQuestion(
                id=question_id,
                question=question_text,
                expected_answerable=expected_answerable,
            )
        )

    return questions


def _compact_sources(raw_sources: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_sources, list):
        return []

    result = []
    for source in raw_sources:
        if not isinstance(source, dict):
            continue
        metadata = source.get("metadata")
        external_id = (
            metadata.get("external_id") if isinstance(metadata, dict) else None
        )
        result.append(
            {
                "citation_id": source.get("citation_id"),
                "chunk_id": source.get("chunk_id"),
                "document_id": source.get("document_id"),
                "title": source.get("title"),
                "source_type": source.get("source_type"),
                "external_id": external_id,
                "score": source.get("score"),
                "reranker_score": source.get("reranker_score"),
            }
        )
    return result


class QueryBatchRunner:
    def __init__(
        self,
        *,
        client: httpx.Client,
        endpoint: str,
        top_k: int,
        strategy: str,
        reranker_enabled: bool,
    ) -> None:
        self.client = client
        self.endpoint = endpoint
        self.top_k = top_k
        self.strategy = strategy
        self.reranker_enabled = reranker_enabled

    def run_question(
        self,
        *,
        question: BatchQuestion,
        sequence: int,
        iteration: int,
    ) -> BatchResult:
        started_at = time.perf_counter()
        try:
            response = self.client.post(
                self.endpoint,
                json={
                    "query": question.question,
                    "top_k": self.top_k,
                    "strategy": self.strategy,
                    "rerank": self.reranker_enabled,
                },
            )
            elapsed_ms = int((time.perf_counter() - started_at) * 1000)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("API response is not a JSON object.")

            metadata = payload.get("metadata")
            if not isinstance(metadata, dict):
                metadata = {}
            sources = _compact_sources(payload.get("sources"))

            return BatchResult(
                sequence=sequence,
                iteration=iteration,
                question_id=question.id,
                question=question.question,
                expected_answerable=question.expected_answerable,
                status="success",
                http_status=response.status_code,
                elapsed_ms=elapsed_ms,
                api_latency_ms=metadata.get("latency_ms"),
                is_answerable=payload.get("is_answerable"),
                confidence=payload.get("confidence"),
                sources_count=len(sources),
                cited_source_ids=metadata.get("cited_source_ids", []),
                provider=metadata.get("llm_provider"),
                retrieval_strategy=metadata.get("retrieval_strategy"),
                reranker_enabled=metadata.get("reranker_enabled"),
                reranker_applied=metadata.get("reranker_applied"),
                reranker_latency_ms=metadata.get("reranker_latency_ms"),
                fallback_used=metadata.get("fallback_used"),
                rejection_reason=metadata.get("rejection_reason"),
                answer=payload.get("answer"),
                sources=sources,
            )
        except (httpx.HTTPError, ValueError) as exc:
            elapsed_ms = int((time.perf_counter() - started_at) * 1000)
            status_code = None
            if isinstance(exc, httpx.HTTPStatusError):
                status_code = exc.response.status_code
            return BatchResult(
                sequence=sequence,
                iteration=iteration,
                question_id=question.id,
                question=question.question,
                expected_answerable=question.expected_answerable,
                status="error",
                http_status=status_code,
                elapsed_ms=elapsed_ms,
                error=str(exc),
            )


def _nearest_rank_percentile(values: list[int], percentile: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[rank - 1]


def summarize_batch(
    results: list[BatchResult],
    *,
    planned_requests: int,
    interrupted: bool,
) -> dict[str, Any]:
    successful = [result for result in results if result.status == "success"]
    latencies = [result.elapsed_ms for result in successful]
    answers = [result for result in successful if result.is_answerable]
    no_answers = [result for result in successful if result.is_answerable is False]
    with_sources = [result for result in answers if result.sources_count > 0]
    expected = [
        result
        for result in successful
        if result.expected_answerable is not None
    ]
    answerability_correct = [
        result
        for result in expected
        if result.expected_answerable == result.is_answerable
    ]
    providers = Counter(result.provider or "unknown" for result in successful)

    def rate(numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 4) if denominator else 0.0

    return {
        "planned_requests": planned_requests,
        "completed_requests": len(results),
        "successful_requests": len(successful),
        "failed_requests": len(results) - len(successful),
        "interrupted": interrupted,
        "answers": len(answers),
        "no_answers": len(no_answers),
        "answer_rate": rate(len(answers), len(successful)),
        "no_answer_rate": rate(len(no_answers), len(successful)),
        "answers_with_sources_rate": rate(len(with_sources), len(answers)),
        "fallback_count": sum(bool(result.fallback_used) for result in successful),
        "reranker_applied_count": sum(
            bool(result.reranker_applied) for result in successful
        ),
        "answerability_accuracy": (
            rate(len(answerability_correct), len(expected)) if expected else None
        ),
        "average_latency_ms": (
            round(sum(latencies) / len(latencies)) if latencies else None
        ),
        "p50_latency_ms": _nearest_rank_percentile(latencies, 0.50),
        "p95_latency_ms": _nearest_rank_percentile(latencies, 0.95),
        "providers": dict(sorted(providers.items())),
    }


def save_batch_report(
    *,
    output_path: Path,
    config: dict[str, Any],
    summary: dict[str, Any],
    results: list[BatchResult],
) -> None:
    import json

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "config": config,
        "summary": summary,
        "results": [asdict(result) for result in results],
    }
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
