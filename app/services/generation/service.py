from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.config import settings
from app.services.generation.llm_provider import (
    LLMGenerationRequest,
    LLMGenerationResult,
    get_configured_llm_provider,
    get_fallback_llm_provider,
)
from app.services.generation.prompt_builder import build_rag_prompt
from app.services.retrieval.retriever import RetrievedChunk


@dataclass
class RAGGenerationResult:
    answer: str
    confidence: float
    provider_name: str
    is_answerable: bool
    cited_source_ids: list[int]
    fallback_used: bool
    fallback_reason: str | None
    rejection_reason: str | None


class RAGGenerationService:
    def generate(
        self,
        *,
        query: str,
        contexts: list[RetrievedChunk],
    ) -> RAGGenerationResult:
        contexts = contexts[: settings.rag_max_contexts]

        if not contexts:
            return self._build_no_answer_result(
                query=query,
                provider_name="retrieval_guard",
                rejection_reason="no_contexts",
            )

        if contexts[0].score < settings.rag_min_retrieval_score:
            return self._build_no_answer_result(
                query=query,
                provider_name="retrieval_guard",
                rejection_reason="low_retrieval_score",
            )

        prompt = build_rag_prompt(
            query=query,
            contexts=contexts,
        )

        request = LLMGenerationRequest(
            query=query,
            contexts=contexts,
            prompt=prompt,
        )

        try:
            provider = get_configured_llm_provider()
            result = provider.generate(request)

            return self._to_rag_result(
                query=query,
                contexts=contexts,
                result=result,
                fallback_used=False,
                fallback_reason=None,
            )

        except Exception as error:
            fallback_provider = get_fallback_llm_provider()
            fallback_result = fallback_provider.generate(request)

            return self._to_rag_result(
                query=query,
                contexts=contexts,
                result=fallback_result,
                fallback_used=True,
                fallback_reason=str(error),
            )

    def _to_rag_result(
        self,
        *,
        query: str,
        contexts: list[RetrievedChunk],
        result: LLMGenerationResult,
        fallback_used: bool,
        fallback_reason: str | None,
    ) -> RAGGenerationResult:
        valid_ids = sorted(
            {
                source_id
                for source_id in result.cited_source_ids
                if 1 <= source_id <= len(contexts)
            }
        )
        markers = {int(value) for value in re.findall(r"\[(\d+)\]", result.answer)}
        invalid_markers = {
            source_id
            for source_id in markers
            if source_id < 1 or source_id > len(contexts)
        }

        if not result.is_answerable:
            return self._build_no_answer_result(
                query=query,
                provider_name=result.provider_name,
                rejection_reason=result.rejection_reason or "model_rejected_context",
                fallback_used=fallback_used,
                fallback_reason=fallback_reason,
            )

        if result.is_answerable and (invalid_markers or not valid_ids):
            return self._build_no_answer_result(
                query=query,
                provider_name=result.provider_name,
                rejection_reason=(
                    "invalid_citations"
                    if invalid_markers
                    else "missing_valid_citations"
                ),
                fallback_used=fallback_used,
                fallback_reason=fallback_reason,
            )

        answer = result.answer.strip()
        if result.is_answerable:
            missing_markers = [
                source_id for source_id in valid_ids if source_id not in markers
            ]
            if missing_markers:
                citations = ", ".join(f"[{source_id}]" for source_id in missing_markers)
                answer = f"{answer}\n\nИсточники: {citations}"

        return RAGGenerationResult(
            answer=answer,
            confidence=result.confidence,
            provider_name=result.provider_name,
            is_answerable=result.is_answerable,
            cited_source_ids=valid_ids,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            rejection_reason=result.rejection_reason,
        )

    def _build_no_answer_result(
        self,
        *,
        query: str,
        provider_name: str,
        rejection_reason: str,
        fallback_used: bool = False,
        fallback_reason: str | None = None,
    ) -> RAGGenerationResult:
        has_cyrillic = bool(re.search(r"[А-Яа-яЁё]", query))
        answer = (
            "В найденных источниках недостаточно информации, чтобы надёжно "
            "ответить на этот вопрос."
            if has_cyrillic
            else (
                "The retrieved sources do not contain enough information "
                "to answer this question reliably."
            )
        )

        return RAGGenerationResult(
            answer=answer,
            confidence=0.0,
            provider_name=provider_name,
            is_answerable=False,
            cited_source_ids=[],
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            rejection_reason=rejection_reason,
        )
