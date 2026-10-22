from __future__ import annotations

import re

from app.services.generation.llm_provider import (
    LLMGenerationRequest,
    LLMGenerationResult,
)
from app.services.retrieval.retriever import RetrievedChunk


class ExtractiveLLMProvider:
    provider_name = "extractive"

    def generate(self, request: LLMGenerationRequest) -> LLMGenerationResult:
        contexts = request.contexts

        if not contexts:
            return LLMGenerationResult(
                answer=(
                    "По базе знаний не найдено достаточно релевантных фрагментов "
                    "для ответа на вопрос."
                ),
                confidence=0.0,
                provider_name=self.provider_name,
                is_answerable=False,
                rejection_reason="no_contexts",
            )

        answer_parts = [
            "На основе найденных источников система нашла следующие сведения:"
        ]

        for index, context in enumerate(contexts[:3], start=1):
            snippet = self._make_snippet(context.content)

            answer_parts.append(f"{index}. {snippet} [{index}]")

        answer_parts.append("")
        answer_parts.append("Источники:")

        for index, context in enumerate(contexts[:3], start=1):
            title = context.title or "Без названия"
            section = (
                f", раздел: {context.section_title}" if context.section_title else ""
            )
            source_type = context.source_type or "unknown_source"

            answer_parts.append(
                f"[{index}] {title}{section} ({source_type}), "
                f"chunk_id={context.chunk_id}, score={context.score:.3f}"
            )

        return LLMGenerationResult(
            answer="\n".join(answer_parts),
            confidence=self._calculate_confidence(contexts),
            provider_name=self.provider_name,
            is_answerable=True,
            cited_source_ids=list(range(1, min(3, len(contexts)) + 1)),
        )

    def _make_snippet(self, text: str, max_length: int = 700) -> str:
        normalized_text = re.sub(r"\s+", " ", text).strip()

        if len(normalized_text) <= max_length:
            return normalized_text

        return normalized_text[:max_length].rstrip() + "..."

    def _calculate_confidence(self, contexts: list[RetrievedChunk]) -> float:
        if not contexts:
            return 0.0

        top_scores = [context.score for context in contexts[:3]]
        average_score = sum(top_scores) / len(top_scores)

        return max(0.0, min(1.0, average_score))
