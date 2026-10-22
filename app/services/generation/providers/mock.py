from app.services.generation.llm_provider import (
    LLMGenerationRequest,
    LLMGenerationResult,
)


class MockLLMProvider:
    provider_name = "mock"

    def generate(self, request: LLMGenerationRequest) -> LLMGenerationResult:
        return LLMGenerationResult(
            answer=(
                "Это тестовый mock-ответ.\n\n"
                f"Вопрос пользователя: {request.query}\n"
                f"Количество найденных источников: {len(request.contexts)}."
            ),
            confidence=0.5,
            provider_name=self.provider_name,
            is_answerable=bool(request.contexts),
            cited_source_ids=[1] if request.contexts else [],
        )
