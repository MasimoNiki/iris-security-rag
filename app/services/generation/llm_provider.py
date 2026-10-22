from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Protocol

from app.core.config import settings
from app.services.retrieval.retriever import RetrievedChunk


@dataclass
class LLMGenerationRequest:
    query: str
    contexts: list[RetrievedChunk]
    prompt: str


@dataclass
class LLMGenerationResult:
    answer: str
    confidence: float
    provider_name: str
    is_answerable: bool = True
    cited_source_ids: list[int] = field(default_factory=list)
    rejection_reason: str | None = None


class LLMProvider(Protocol):
    provider_name: str

    def generate(self, request: LLMGenerationRequest) -> LLMGenerationResult:
        pass


def build_llm_provider(provider_name: str) -> LLMProvider:
    normalized_provider_name = provider_name.strip().lower()

    if normalized_provider_name == "extractive":
        from app.services.generation.providers.extractive import (
            ExtractiveLLMProvider,
        )

        return ExtractiveLLMProvider()

    if normalized_provider_name == "mock":
        from app.services.generation.providers.mock import MockLLMProvider

        return MockLLMProvider()

    if normalized_provider_name == "openai_compatible":
        from app.services.generation.providers.openai_compatible import (
            OpenAICompatibleProvider,
        )

        return OpenAICompatibleProvider()

    if normalized_provider_name == "ollama":
        from app.services.generation.providers.ollama import OllamaProvider

        return OllamaProvider()

    raise ValueError(f"Unsupported LLM provider: {provider_name}")


@lru_cache
def get_configured_llm_provider() -> LLMProvider:
    return build_llm_provider(settings.llm_provider)


@lru_cache
def get_fallback_llm_provider() -> LLMProvider:
    return build_llm_provider(settings.llm_fallback_provider)
