from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


@dataclass
class TextChunk:
    chunk_index: int
    content: str
    token_count: int
    section_title: str | None
    metadata_json: dict[str, Any]


def estimate_token_count(text: str) -> int:
    return len(text.split())


def split_markdown_by_headings(text: str) -> list[tuple[str | None, str]]:
    matches = list(HEADING_PATTERN.finditer(text))

    if not matches:
        return [(None, text.strip())]

    sections: list[tuple[str | None, str]] = []

    preamble = text[: matches[0].start()].strip()

    if preamble:
        sections.append((None, preamble))

    for index, match in enumerate(matches):
        heading = match.group(0).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)

        body = text[start:end].strip()
        section_text = body

        if section_text:
            sections.append((heading, section_text))

    return sections


def split_by_paragraphs(text: str) -> list[str]:
    paragraphs = re.split(r"\n\s*\n", text)

    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def build_chunk_content(
    document_title: str,
    section_title: str | None,
    paragraphs: list[str],
) -> str:
    parts = [f"# {document_title}"]

    if section_title:
        parts.append(section_title)

    parts.extend(paragraphs)

    return "\n\n".join(parts).strip()


def split_long_paragraph(
    paragraph: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    parts: list[str] = []

    start = 0

    while start < len(paragraph):
        end = start + chunk_size
        parts.append(paragraph[start:end].strip())

        if end >= len(paragraph):
            break

        start = max(end - chunk_overlap, start + 1)

    return [part for part in parts if part]


def chunk_markdown_text(
    text: str,
    document_title: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[TextChunk]:
    sections = split_markdown_by_headings(text)

    chunks: list[TextChunk] = []

    for section_title, section_text in sections:
        paragraphs = split_by_paragraphs(section_text)

        current_paragraphs: list[str] = []

        for paragraph in paragraphs:
            candidate_content = build_chunk_content(
                document_title=document_title,
                section_title=section_title,
                paragraphs=[*current_paragraphs, paragraph],
            )

            if len(candidate_content) <= chunk_size:
                current_paragraphs.append(paragraph)
                continue

            if current_paragraphs:
                content = build_chunk_content(
                    document_title=document_title,
                    section_title=section_title,
                    paragraphs=current_paragraphs,
                )

                chunks.append(
                    TextChunk(
                        chunk_index=len(chunks),
                        content=content,
                        token_count=estimate_token_count(content),
                        section_title=section_title,
                        metadata_json={
                            "char_count": len(content),
                            "chunk_size": chunk_size,
                            "chunk_overlap": chunk_overlap,
                        },
                    )
                )

                current_paragraphs = []

            if len(paragraph) > chunk_size:
                for part in split_long_paragraph(
                    paragraph=paragraph,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                ):
                    content = build_chunk_content(
                        document_title=document_title,
                        section_title=section_title,
                        paragraphs=[part],
                    )

                    chunks.append(
                        TextChunk(
                            chunk_index=len(chunks),
                            content=content,
                            token_count=estimate_token_count(content),
                            section_title=section_title,
                            metadata_json={
                                "char_count": len(content),
                                "chunk_size": chunk_size,
                                "chunk_overlap": chunk_overlap,
                                "split_reason": "long_paragraph",
                            },
                        )
                    )
            else:
                current_paragraphs = [paragraph]

        if current_paragraphs:
            content = build_chunk_content(
                document_title=document_title,
                section_title=section_title,
                paragraphs=current_paragraphs,
            )

            chunks.append(
                TextChunk(
                    chunk_index=len(chunks),
                    content=content,
                    token_count=estimate_token_count(content),
                    section_title=section_title,
                    metadata_json={
                        "char_count": len(content),
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                    },
                )
            )

    return chunks
