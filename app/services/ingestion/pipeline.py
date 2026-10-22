from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Chunk, Document
from app.services.ingestion.chunker import chunk_markdown_text
from app.services.ingestion.loaders import find_files, read_text_file
from app.services.ingestion.metadata import DocumentMetadata
from app.services.ingestion.parsers import parse_document


@dataclass
class IngestionResult:
    documents_created: int
    documents_updated: int
    documents_skipped: int
    chunks_created: int


def get_document_by_local_path(db: Session, local_path: str) -> Document | None:
    return db.query(Document).filter(Document.local_path == local_path).first()


def build_document_values(
    metadata: DocumentMetadata,
) -> dict[str, Any]:
    """Преобразует разобранные метаданные в поля модели Document."""
    return {
        "title": metadata.title,
        "source_type": metadata.source_type,
        "external_id": metadata.external_id,
        "source_url": metadata.source_url,
        "local_path": metadata.local_path,
        "language": metadata.language,
        "domain": metadata.domain,
        "checksum": metadata.checksum,
        "source_revision": metadata.source_revision,
        "metadata_json": metadata.metadata_json,
    }


def document_values_changed(
    document: Document,
    document_values: dict[str, Any],
) -> bool:
    """Проверяет, отличаются ли поля документа от разобранных метаданных."""
    return any(
        getattr(document, field_name) != field_value
        for field_name, field_value in document_values.items()
    )


def apply_document_values(
    document: Document,
    document_values: dict[str, Any],
) -> None:
    """Обновляет поля существующего документа."""
    for field_name, field_value in document_values.items():
        setattr(document, field_name, field_value)


def build_chunk_metadata(
    *,
    current_metadata: dict[str, Any] | None,
    document: Document,
    tags: list[str],
) -> dict[str, Any]:
    """Формирует актуальный metadata_json чанка."""
    return {
        **(current_metadata or {}),
        "document_title": document.title,
        "source_type": document.source_type,
        "language": document.language,
        "domain": document.domain,
        "tags": tags,
        "local_path": document.local_path,
        "external_id": document.external_id,
        "source_url": document.source_url,
        "source_revision": document.source_revision,
    }


def refresh_existing_chunk_metadata(
    *,
    document: Document,
    tags: list[str],
) -> None:
    """Обновляет payload существующих чанков без изменения их ID."""
    for chunk in document.chunks:
        chunk.metadata_json = build_chunk_metadata(
            current_metadata=chunk.metadata_json,
            document=document,
            tags=tags,
        )


def create_chunks_for_document(
    db: Session,
    *,
    document: Document,
    document_text: str,
    tags: list[str],
) -> int:
    chunks = chunk_markdown_text(
        text=document_text,
        document_title=document.title,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    for chunk in chunks:
        metadata_json = build_chunk_metadata(
            current_metadata=chunk.metadata_json,
            document=document,
            tags=tags,
        )

        db_chunk = Chunk(
            document_id=document.id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            token_count=chunk.token_count,
            section_title=chunk.section_title,
            metadata_json=metadata_json,
        )

        db.add(db_chunk)

    return len(chunks)


def ingest_file(db: Session, file_path: Path) -> tuple[str, int]:
    raw_text = read_text_file(file_path)
    parsed_document = parse_document(
        file_path=file_path,
        raw_text=raw_text,
    )

    metadata = parsed_document.metadata
    document_values = build_document_values(metadata)
    existing_document = get_document_by_local_path(
        db=db,
        local_path=metadata.local_path,
    )

    if existing_document is not None:
        content_changed = existing_document.checksum != metadata.checksum
        metadata_changed = document_values_changed(
            existing_document,
            document_values,
        )

        if not metadata_changed:
            return "skipped", 0

        apply_document_values(
            existing_document,
            document_values,
        )

        if not content_changed:
            refresh_existing_chunk_metadata(
                document=existing_document,
                tags=metadata.tags,
            )
            return "updated", 0

        for chunk in list(existing_document.chunks):
            db.delete(chunk)

        db.flush()
        document = existing_document
        status = "updated"
    else:
        document = Document(**document_values)
        db.add(document)
        db.flush()
        status = "created"

    chunks_created = create_chunks_for_document(
        db=db,
        document=document,
        document_text=parsed_document.text,
        tags=metadata.tags,
    )

    return status, chunks_created


def ingest_local_documents(db: Session, raw_data_dir: Path) -> IngestionResult:
    files = find_files(raw_data_dir)

    documents_created = 0
    documents_updated = 0
    documents_skipped = 0
    chunks_created = 0

    for file_path in files:
        status, file_chunks_created = ingest_file(
            db=db,
            file_path=file_path,
        )

        if status == "created":
            documents_created += 1
        elif status == "updated":
            documents_updated += 1
        elif status == "skipped":
            documents_skipped += 1
        else:
            raise ValueError(f"Unknown ingestion status: {status}")

        chunks_created += file_chunks_created

    db.commit()

    return IngestionResult(
        documents_created=documents_created,
        documents_updated=documents_updated,
        documents_skipped=documents_skipped,
        chunks_created=chunks_created,
    )
