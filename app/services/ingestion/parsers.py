from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.services.ingestion.metadata import (
    DocumentMetadata,
    build_document_metadata,
    extract_front_matter,
)


@dataclass
class ParsedDocument:
    metadata: DocumentMetadata
    text: str


def parse_markdown_document(file_path: Path, raw_text: str) -> ParsedDocument:
    front_matter, body_text = extract_front_matter(raw_text)

    metadata = build_document_metadata(
        file_path=file_path,
        raw_text=raw_text,
        front_matter=front_matter,
        body_text=body_text,
    )

    return ParsedDocument(
        metadata=metadata,
        text=body_text,
    )


def parse_document(file_path: Path, raw_text: str) -> ParsedDocument:
    suffix = file_path.suffix.lower()

    if suffix == ".md":
        return parse_markdown_document(
            file_path=file_path,
            raw_text=raw_text,
        )

    raise ValueError(f"Unsupported file type: {suffix}")
