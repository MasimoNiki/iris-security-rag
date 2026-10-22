from __future__ import annotations

import json
import re
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import settings
from app.services.evaluation.dataset import GoldenQuestion
from app.services.evaluation.metrics import (
    EvalQuestionResult,
    EvalSummary,
    calculate_keyword_recall,
    find_first_content_rank,
    find_first_document_rank,
    get_chunk_external_id,
    get_matched_keywords,
    summarize_eval_results,
)
from app.services.generation.service import RAGGenerationService
from app.services.retrieval.retriever import RetrievedChunk, get_retriever

NO_ANSWER_MARKERS = (
    "не найдено достаточно релевантных",
    "недостаточно информации",
    "недостаточно контекста",
    "не могу ответить",
    "not enough information",
    "insufficient information",
    "insufficient context",
    "cannot answer",
)


class EvaluationRunner:
    def __init__(
        self,
        top_k: int = 5,
        no_answer_threshold: float = 0.01,
        retrieval_strategy: str | None = None,
        reranker_enabled: bool | None = None,
    ) -> None:
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        if not 0.0 <= no_answer_threshold <= 1.0:
            raise ValueError(
                "no_answer_threshold must be between 0 and 1.",
            )

        self.top_k = top_k
        self.no_answer_threshold = no_answer_threshold
        self.retrieval_strategy = retrieval_strategy or settings.retrieval_strategy
        self.reranker_enabled = (
            settings.reranker_enabled if reranker_enabled is None else reranker_enabled
        )
        self.retriever = get_retriever(
            self.retrieval_strategy,
            reranker_enabled=self.reranker_enabled,
        )
        self.generation_service = RAGGenerationService()

    def run(
        self,
        questions: list[GoldenQuestion],
    ) -> tuple[EvalSummary, list[EvalQuestionResult]]:
        results = [self.evaluate_question(question) for question in questions]
        summary = summarize_eval_results(
            results=results,
            top_k=self.top_k,
            no_answer_threshold=self.no_answer_threshold,
            retrieval_strategy=self.retrieval_strategy,
            reranker_enabled=self.reranker_enabled,
        )

        return summary, results

    def evaluate_question(
        self,
        question: GoldenQuestion,
    ) -> EvalQuestionResult:
        started_at = time.perf_counter()
        retrieved_chunks = self.retriever.search(
            query=question.question,
            top_k=self.top_k,
        )
        generation_result = self.generation_service.generate(
            query=question.question,
            contexts=retrieved_chunks,
        )
        latency_ms = int((time.perf_counter() - started_at) * 1000)

        matched_keywords = get_matched_keywords(
            chunks=retrieved_chunks,
            expected_keywords=question.expected_source_keywords,
        )
        first_document_rank = find_first_document_rank(
            chunks=retrieved_chunks,
            expected_external_ids=question.expected_external_ids,
            expected_local_paths=question.expected_local_paths,
        )
        first_content_rank = find_first_content_rank(
            chunks=retrieved_chunks,
            expected_keywords=question.expected_source_keywords,
            min_keyword_matches=question.min_keyword_matches,
        )

        if question.has_document_expectation:
            first_relevant_rank = first_document_rank
        else:
            first_relevant_rank = first_content_rank

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
        hit = bool(question.answerable and first_relevant_rank is not None)
        reciprocal_rank = 1 / first_relevant_rank if first_relevant_rank else 0.0
        document_reciprocal_rank = (
            1 / first_document_rank if first_document_rank else 0.0
        )
        content_reciprocal_rank = 1 / first_content_rank if first_content_rank else 0.0
        keyword_recall = calculate_keyword_recall(
            matched_keywords=matched_keywords,
            expected_keywords=question.expected_source_keywords,
        )
        no_answer = not generation_result.is_answerable
        answer_has_sources = bool(
            generation_result.is_answerable and generation_result.cited_source_ids
        )
        answerability_correct = not no_answer if question.answerable else no_answer
        reranker_applied = any(
            chunk.reranker_score is not None for chunk in retrieved_chunks
        )
        reranker_latency_ms = next(
            (
                chunk.reranker_latency_ms
                for chunk in retrieved_chunks
                if chunk.reranker_latency_ms is not None
            ),
            None,
        )

        return EvalQuestionResult(
            question_id=question.id,
            question=question.question,
            language=question.language,
            tags=question.tags,
            answerable=question.answerable,
            hit=hit,
            document_hit=document_hit,
            content_hit=content_hit,
            reciprocal_rank=reciprocal_rank,
            document_reciprocal_rank=document_reciprocal_rank,
            content_reciprocal_rank=content_reciprocal_rank,
            first_relevant_rank=first_relevant_rank,
            first_document_rank=first_document_rank,
            first_content_rank=first_content_rank,
            keyword_recall=keyword_recall,
            latency_ms=latency_ms,
            answer_has_sources=answer_has_sources,
            no_answer=no_answer,
            answerability_correct=answerability_correct,
            reranker_applied=reranker_applied,
            reranker_latency_ms=reranker_latency_ms,
            matched_keywords=matched_keywords,
            expected_source_keywords=question.expected_source_keywords,
            expected_external_ids=question.expected_external_ids,
            expected_local_paths=question.expected_local_paths,
            provider_name=generation_result.provider_name,
            generation_confidence=generation_result.confidence,
            generated_is_answerable=generation_result.is_answerable,
            rejection_reason=generation_result.rejection_reason,
            cited_source_ids=generation_result.cited_source_ids,
            fallback_used=generation_result.fallback_used,
            answer=generation_result.answer,
            top_results=self._build_top_results(retrieved_chunks),
        )

    def _is_no_answer(
        self,
        *,
        answer: str,
        confidence: float,
        chunks: list[RetrievedChunk],
    ) -> bool:
        if not chunks or confidence <= self.no_answer_threshold:
            return True

        normalized_answer = re.sub(r"\s+", " ", answer.lower()).strip()

        return any(marker in normalized_answer for marker in NO_ANSWER_MARKERS)

    def _answer_has_sources(
        self,
        *,
        answer: str,
        chunks: list[RetrievedChunk],
    ) -> bool:
        return bool(chunks and re.search(r"\[\d+\]", answer))

    def _build_top_results(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[dict]:
        return [
            {
                "rank": index,
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "title": chunk.title,
                "source_type": chunk.source_type,
                "external_id": get_chunk_external_id(chunk),
                "section_title": chunk.section_title,
                "score": chunk.score,
                "dense_score": chunk.dense_score,
                "lexical_score": chunk.lexical_score,
                "fusion_score": chunk.fusion_score,
                "dense_rank": chunk.dense_rank,
                "lexical_rank": chunk.lexical_rank,
                "pre_rerank_rank": chunk.pre_rerank_rank,
                "reranker_score": chunk.reranker_score,
                "reranker_rank": chunk.reranker_rank,
                "reranker_latency_ms": chunk.reranker_latency_ms,
                "retrieval_strategy": chunk.retrieval_strategy,
                "local_path": chunk.local_path,
            }
            for index, chunk in enumerate(chunks, start=1)
        ]


def save_eval_report(
    *,
    output_path: Path,
    summary: EvalSummary,
    results: list[EvalQuestionResult],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "schema_version": 3,
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": asdict(summary),
        "results": [asdict(result) for result in results],
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )
