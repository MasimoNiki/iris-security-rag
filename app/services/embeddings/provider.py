from __future__ import annotations

from functools import cached_property

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingProvider:
    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    @property
    def dimension(self) -> int:
        raise NotImplementedError


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.embedding_model_name
        self.model = SentenceTransformer(self.model_name)

    def embed_query(self, text: str) -> list[float]:
        vector = self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return vector.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return [vector.tolist() for vector in vectors]

    @cached_property
    def dimension(self) -> int:
        model_dimension = self.model.get_sentence_embedding_dimension()

        if model_dimension is not None:
            return int(model_dimension)

        return len(self.embed_query("dimension test"))
