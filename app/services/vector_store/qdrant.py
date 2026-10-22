from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient
from qdrant_client import models as qdrant_models

from app.core.config import settings


class QdrantVectorStore:
    def __init__(
        self,
        url: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        self.url = url or settings.qdrant_url
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.client = QdrantClient(url=self.url)

    def collection_exists(self) -> bool:
        collections = self.client.get_collections().collections

        return any(
            collection.name == self.collection_name for collection in collections
        )

    def create_collection(self, vector_size: int) -> None:
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=vector_size,
                distance=qdrant_models.Distance.COSINE,
            ),
        )

    def ensure_collection(self, vector_size: int) -> None:
        if self.collection_exists():
            return

        self.create_collection(vector_size)

    def recreate_collection(self, vector_size: int) -> None:
        """Удаляет существующую коллекцию и создаёт пустую заново."""
        if self.collection_exists():
            self.client.delete_collection(
                collection_name=self.collection_name,
            )

        self.create_collection(vector_size)

    def upsert_vectors(
        self,
        *,
        ids: list[int],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
    ) -> None:
        points = [
            qdrant_models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
            for point_id, vector, payload in zip(
                ids,
                vectors,
                payloads,
                strict=True,
            )
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

    def search(
        self,
        *,
        query_vector: list[float],
        top_k: int,
    ) -> list[Any]:
        if not self.collection_exists():
            return []

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        return response.points

    def close(self) -> None:
        self.client.close()
