from typing import Any

from sqlalchemy.orm import Session

from app.db.models import Chunk


def create_chunk(
    db: Session,
    *,
    document_id: int,
    chunk_index: int,
    content: str,
    token_count: int | None = None,
    section_title: str | None = None,
    metadata_json: dict[str, Any] | None = None,
) -> Chunk:
    chunk = Chunk(
        document_id=document_id,
        chunk_index=chunk_index,
        content=content,
        token_count=token_count,
        section_title=section_title,
        metadata_json=metadata_json,
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    return chunk
