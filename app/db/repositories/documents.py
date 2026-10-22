from sqlalchemy.orm import Session

from app.db.models import Document


def create_document(
    db: Session,
    *,
    title: str,
    source_type: str,
    source_url: str | None = None,
    local_path: str | None = None,
    language: str | None = None,
    checksum: str | None = None,
) -> Document:
    document = Document(
        title=title,
        source_type=source_type,
        source_url=source_url,
        local_path=local_path,
        language=language,
        checksum=checksum,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_document_by_id(db: Session, document_id: int) -> Document | None:
    return db.get(Document, document_id)
