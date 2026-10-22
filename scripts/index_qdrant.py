from __future__ import annotations

import argparse
from collections.abc import Iterator

from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.db.models import Chunk
from app.db.session import SessionLocal
from app.services.embeddings.provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.services.vector_store.qdrant import QdrantVectorStore

BATCH_SIZE = 32


def build_payload(chunk: Chunk) -> dict:
    document = chunk.document

    return {
        "chunk_id": chunk.id,
        "document_id": chunk.document_id,
        "chunk_index": chunk.chunk_index,
        "content": chunk.content,
        "token_count": chunk.token_count,
        "section_title": chunk.section_title,
        "document_title": document.title if document else None,
        "source_type": document.source_type if document else None,
        "external_id": document.external_id if document else None,
        "source_url": document.source_url if document else None,
        "source_revision": (document.source_revision if document else None),
        "local_path": document.local_path if document else None,
        "language": document.language if document else None,
        "domain": document.domain if document else None,
        "document_metadata": (document.metadata_json if document else {}),
        "chunk_metadata": chunk.metadata_json or {},
    }


def iter_batches(
    items: list[Chunk],
    batch_size: int,
) -> Iterator[list[Chunk]]:
    for index in range(0, len(items), batch_size):
        yield items[index : index + batch_size]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Index PostgreSQL chunks in Qdrant.",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help=(
            "Delete the current collection before indexing. "
            "PostgreSQL data is not changed."
        ),
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    with SessionLocal() as db:
        chunks = (
            db.query(Chunk).options(joinedload(Chunk.document)).order_by(Chunk.id).all()
        )

    if not chunks:
        print("No chunks found in PostgreSQL.")
        print("Run first: python scripts/ingest_local_docs.py")
        return

    embedding_provider = SentenceTransformerEmbeddingProvider()
    vector_store = QdrantVectorStore()

    try:
        if arguments.recreate:
            print(f"Recreating Qdrant collection: {settings.qdrant_collection_name}")
            vector_store.recreate_collection(
                vector_size=embedding_provider.dimension,
            )
        else:
            vector_store.ensure_collection(
                vector_size=embedding_provider.dimension,
            )

        indexed_count = 0

        for batch in iter_batches(chunks, BATCH_SIZE):
            texts = [chunk.content for chunk in batch]
            vectors = embedding_provider.embed_documents(texts)

            ids = [chunk.id for chunk in batch]
            payloads = [build_payload(chunk) for chunk in batch]

            vector_store.upsert_vectors(
                ids=ids,
                vectors=vectors,
                payloads=payloads,
            )

            indexed_count += len(batch)
            print(f"Indexed chunks: {indexed_count}/{len(chunks)}")

        print("Qdrant indexing finished")
        print(f"Collection: {settings.qdrant_collection_name}")
        print(f"Vector size: {embedding_provider.dimension}")
        print(f"Total chunks indexed: {indexed_count}")

        if not arguments.recreate:
            print("Existing points were preserved. Use --recreate for a full rebuild.")
    finally:
        vector_store.close()


if __name__ == "__main__":
    main()
