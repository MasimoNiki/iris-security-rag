from __future__ import annotations

import json

import httpx

from app.services.generation.llm_provider import LLMGenerationRequest
from app.services.generation.providers.ollama import OllamaProvider
from app.services.generation.service import RAGGenerationService
from app.services.retrieval.retriever import RetrievedChunk


def make_context(score: float = 0.8) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=10,
        document_id=20,
        chunk_index=0,
        title="Credential Dumping",
        content="Credential dumping can target LSASS memory.",
        score=score,
        source_type="mitre_attack",
        local_path="data/raw/mitre/t1003.md",
        language="en",
        section_title="Description",
        metadata={},
    )


def test_ollama_provider_parses_structured_answer() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["model"]
        assert payload["stream"] is False
        assert payload["think"] is False
        assert payload["format"]["type"] == "object"

        return httpx.Response(
            200,
            json={
                "message": {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "answer": "LSASS may be targeted [1].",
                            "is_answerable": True,
                            "confidence": 0.9,
                            "citations": [1],
                        }
                    ),
                }
            },
        )

    contexts = [make_context()]
    provider = OllamaProvider(transport=httpx.MockTransport(handler))
    result = provider.generate(
        LLMGenerationRequest(
            query="What can be targeted?",
            contexts=contexts,
            prompt="test prompt",
        )
    )

    assert result.is_answerable is True
    assert result.cited_source_ids == [1]
    assert result.confidence == 0.8
    assert "[1]" in result.answer


def test_ollama_provider_rejects_unknown_citation() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "message": {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "answer": "Unsupported claim [9].",
                            "is_answerable": True,
                            "confidence": 0.9,
                            "citations": [9],
                        }
                    ),
                }
            },
        )

    provider = OllamaProvider(transport=httpx.MockTransport(handler))
    result = provider.generate(
        LLMGenerationRequest(
            query="Question",
            contexts=[make_context()],
            prompt="test prompt",
        )
    )

    assert result.is_answerable is False
    assert result.rejection_reason == "invalid_citations"


def test_generation_service_rejects_low_retrieval_score() -> None:
    result = RAGGenerationService().generate(
        query="What happened?",
        contexts=[make_context(score=0.2)],
    )

    assert result.is_answerable is False
    assert result.provider_name == "retrieval_guard"
    assert result.rejection_reason == "low_retrieval_score"
    assert result.cited_source_ids == []


def test_generation_service_uses_language_for_no_answer() -> None:
    result = RAGGenerationService().generate(
        query="Какая внутренняя политика действует?",
        contexts=[],
    )

    assert result.is_answerable is False
    assert result.answer.startswith("В найденных источниках")
