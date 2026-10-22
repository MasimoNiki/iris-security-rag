from __future__ import annotations

import re

import httpx

from app.core.config import settings
from app.services.generation.llm_provider import (
    LLMGenerationRequest,
    LLMGenerationResult,
)
from app.services.retrieval.retriever import RetrievedChunk


class OpenAICompatibleProvider:
    provider_name = "openai_compatible"

    def generate(self, request: LLMGenerationRequest) -> LLMGenerationResult:
        if not settings.openai_compatible_base_url:
            raise RuntimeError("OPENAI_COMPATIBLE_BASE_URL is not configured")

        if not settings.openai_compatible_model:
            raise RuntimeError("OPENAI_COMPATIBLE_MODEL is not configured")

        base_url = settings.openai_compatible_base_url.rstrip("/")
        url = f"{base_url}/chat/completions"

        headers = {
            "Content-Type": "application/json",
        }

        if settings.openai_compatible_api_key:
            headers["Authorization"] = f"Bearer {settings.openai_compatible_api_key}"

        payload = {
            "model": settings.openai_compatible_model,
            "temperature": settings.llm_temperature,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты — помощник SOC-аналитика. "
                        "Отвечай только на основе предоставленных источников."
                    ),
                },
                {
                    "role": "user",
                    "content": request.prompt,
                },
            ],
        }

        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            response = client.post(
                url,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        response_data = response.json()
        answer = response_data["choices"][0]["message"]["content"]
        cited_source_ids = sorted(
            {
                int(match)
                for match in re.findall(r"\[(\d+)\]", answer)
                if 1 <= int(match) <= len(request.contexts)
            }
        )

        return LLMGenerationResult(
            answer=answer,
            confidence=self._calculate_confidence(request.contexts),
            provider_name=self.provider_name,
            is_answerable=bool(cited_source_ids),
            cited_source_ids=cited_source_ids,
            rejection_reason=None if cited_source_ids else "missing_valid_citations",
        )

    def _calculate_confidence(self, contexts: list[RetrievedChunk]) -> float:
        if not contexts:
            return 0.0

        top_scores = [context.score for context in contexts[:3]]
        average_score = sum(top_scores) / len(top_scores)

        return max(0.0, min(1.0, average_score))
