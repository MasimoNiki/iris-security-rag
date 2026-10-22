from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Chunk, Document
from app.db.session import SessionLocal


OUTPUT_PATH = Path("data/audit/latest_corpus_audit.json")
DETAIL_LIMIT = 100

LEGACY_SOURCE_TYPES = {
    "mitre",
    "mitre_summary",
    "owasp",
    "owasp_summary",
    "nist_summary",
    "synthetic_runbook",
}

COMMON_REQUIRED_METADATA_FIELDS = {
    "language",
    "domain",
    "checksum",
    "local_path",
    "tags",
}

PROVENANCE_REQUIRED_SOURCE_TYPES = {
    "mitre_attack",
    "nist",
    "owasp_top10",
    "sigma_rule",
}

PROVENANCE_REQUIRED_METADATA_FIELDS = {
    "external_id",
    "source_url",
    "source_revision",
}


def is_blank(value: Any) -> bool:
    """Проверяет, отсутствует ли значение метаданных."""
    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    return False


def calculate_percentage(value: int, total: int) -> float:
    """Вычисляет процент с округлением до двух знаков."""
    if total == 0:
        return 0.0

    return round(value / total * 100, 2)


def document_summary(document: Document) -> dict[str, Any]:
    """Возвращает краткую информацию о документе."""
    return {
        "id": document.id,
        "title": document.title,
        "source_type": document.source_type,
        "external_id": document.external_id,
        "local_path": document.local_path,
    }


def find_duplicate_groups(
    documents: list[Document],
    attribute_name: str,
    include_source_type: bool = False,
) -> list[dict[str, Any]]:
    """Находит документы с одинаковым значением выбранного поля."""
    groups: defaultdict[str, list[Document]] = defaultdict(list)

    for document in documents:
        value = getattr(document, attribute_name)

        if is_blank(value):
            continue

        normalized_value = str(value).strip()

        if include_source_type:
            group_key = f"{document.source_type}:{normalized_value}"
        else:
            group_key = normalized_value

        groups[group_key].append(document)

    duplicate_groups = []

    for value, grouped_documents in groups.items():
        if len(grouped_documents) < 2:
            continue

        duplicate_groups.append(
            {
                "value": value,
                "count": len(grouped_documents),
                "documents": [
                    document_summary(document) for document in grouped_documents
                ],
            }
        )

    return sorted(
        duplicate_groups,
        key=lambda item: (-item["count"], item["value"]),
    )


def collect_postgres_report(
    session: Session,
) -> tuple[dict[str, Any], set[int]]:
    """Собирает сведения о документах и чанках в PostgreSQL."""
    chunk_counts_subquery = (
        select(
            Chunk.document_id,
            func.count(Chunk.id).label("chunk_count"),
        )
        .group_by(Chunk.document_id)
        .subquery()
    )

    statement = (
        select(
            Document,
            func.coalesce(
                chunk_counts_subquery.c.chunk_count,
                0,
            ).label("chunk_count"),
        )
        .outerjoin(
            chunk_counts_subquery,
            chunk_counts_subquery.c.document_id == Document.id,
        )
        .order_by(Document.id)
    )

    document_rows = session.execute(statement).all()
    documents = [row[0] for row in document_rows]

    chunk_ids = set(
        session.scalars(
            select(Chunk.id).order_by(Chunk.id),
        ).all()
    )

    documents_by_source_type: Counter[str] = Counter()
    chunks_by_source_type: Counter[str] = Counter()

    documents_without_chunks = []
    missing_metadata = {
        "external_id": [],
        "source_url": [],
        "language": [],
        "domain": [],
        "checksum": [],
        "local_path": [],
        "source_revision": [],
        "tags": [],
    }
    missing_required_metadata = {
        field_name: []
        for field_name in (
            COMMON_REQUIRED_METADATA_FIELDS | PROVENANCE_REQUIRED_METADATA_FIELDS
        )
    }

    for document, chunk_count in document_rows:
        source_type = document.source_type or "<missing>"

        documents_by_source_type[source_type] += 1
        chunks_by_source_type[source_type] += int(chunk_count)

        if chunk_count == 0:
            documents_without_chunks.append(document_summary(document))

        for field_name in (
            "external_id",
            "source_url",
            "language",
            "domain",
            "checksum",
            "local_path",
            "source_revision",
        ):
            if is_blank(getattr(document, field_name)):
                summary = document_summary(document)
                missing_metadata[field_name].append(summary)

                if field_name in COMMON_REQUIRED_METADATA_FIELDS:
                    missing_required_metadata[field_name].append(summary)

                if (
                    source_type in PROVENANCE_REQUIRED_SOURCE_TYPES
                    and field_name in PROVENANCE_REQUIRED_METADATA_FIELDS
                ):
                    missing_required_metadata[field_name].append(summary)

        metadata_json = document.metadata_json or {}
        tags = metadata_json.get("tags")

        if not tags:
            summary = document_summary(document)
            missing_metadata["tags"].append(summary)
            missing_required_metadata["tags"].append(summary)

    document_count = len(documents)
    chunk_count = len(chunk_ids)

    missing_metadata_report = {}
    missing_required_metadata_report = {}

    for field_name, affected_documents in missing_metadata.items():
        missing_metadata_report[field_name] = {
            "count": len(affected_documents),
            "percentage": calculate_percentage(
                len(affected_documents),
                document_count,
            ),
            "documents": affected_documents[:DETAIL_LIMIT],
        }

    for field_name, affected_documents in missing_required_metadata.items():
        missing_required_metadata_report[field_name] = {
            "count": len(affected_documents),
            "percentage": calculate_percentage(
                len(affected_documents),
                document_count,
            ),
            "documents": affected_documents[:DETAIL_LIMIT],
        }

    legacy_source_types = {
        source_type: count
        for source_type, count in documents_by_source_type.items()
        if source_type in LEGACY_SOURCE_TYPES
    }

    report = {
        "document_count": document_count,
        "chunk_count": chunk_count,
        "average_chunks_per_document": (
            round(chunk_count / document_count, 2) if document_count else 0.0
        ),
        "documents_by_source_type": dict(sorted(documents_by_source_type.items())),
        "chunks_by_source_type": dict(sorted(chunks_by_source_type.items())),
        "legacy_source_types": legacy_source_types,
        "documents_without_chunks": {
            "count": len(documents_without_chunks),
            "documents": documents_without_chunks[:DETAIL_LIMIT],
        },
        "missing_metadata": missing_metadata_report,
        "missing_required_metadata": missing_required_metadata_report,
        "duplicates": {
            "checksum": find_duplicate_groups(
                documents,
                "checksum",
            ),
            "local_path": find_duplicate_groups(
                documents,
                "local_path",
            ),
            "external_id": find_duplicate_groups(
                documents,
                "external_id",
                include_source_type=True,
            ),
        },
    }

    return report, chunk_ids


def coerce_chunk_id(value: Any) -> int | None:
    """Пытается преобразовать идентификатор точки в ID чанка."""
    if value is None or isinstance(value, bool):
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def extract_chunk_id_from_point(point: Any) -> int | None:
    """Получает chunk_id из payload или идентификатора точки."""
    payload = point.payload or {}

    chunk_id = coerce_chunk_id(
        payload.get("chunk_id"),
    )

    if chunk_id is not None:
        return chunk_id

    return coerce_chunk_id(point.id)


def collect_qdrant_report(
    database_chunk_ids: set[int],
) -> dict[str, Any]:
    """Проверяет коллекцию Qdrant и сопоставляет точки с чанками."""
    client = QdrantClient(
        url=str(settings.qdrant_url),
    )

    collection_name = settings.qdrant_collection_name
    qdrant_chunk_ids: set[int] = set()
    unmapped_point_ids: list[str] = []

    try:
        collections_response = client.get_collections()

        collection_names = {
            collection.name for collection in collections_response.collections
        }

        if collection_name not in collection_names:
            return {
                "available": True,
                "collection_exists": False,
                "collection_name": collection_name,
                "points_count": 0,
                "mapped_chunk_ids_count": 0,
                "unmapped_point_ids": [],
                "missing_in_qdrant": sorted(database_chunk_ids),
                "extra_in_qdrant": [],
                "error": None,
            }

        collection_info = client.get_collection(
            collection_name=collection_name,
        )

        offset = None
        seen_offsets = set()

        while True:
            points, next_offset = client.scroll(
                collection_name=collection_name,
                limit=256,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            for point in points:
                chunk_id = extract_chunk_id_from_point(point)

                if chunk_id is None:
                    unmapped_point_ids.append(str(point.id))
                else:
                    qdrant_chunk_ids.add(chunk_id)

            if next_offset is None:
                break

            offset_marker = str(next_offset)

            if offset_marker in seen_offsets:
                break

            seen_offsets.add(offset_marker)
            offset = next_offset

        missing_in_qdrant = sorted(database_chunk_ids - qdrant_chunk_ids)
        extra_in_qdrant = sorted(qdrant_chunk_ids - database_chunk_ids)

        return {
            "available": True,
            "collection_exists": True,
            "collection_name": collection_name,
            "points_count": getattr(
                collection_info,
                "points_count",
                None,
            ),
            "indexed_vectors_count": getattr(
                collection_info,
                "indexed_vectors_count",
                None,
            ),
            "mapped_chunk_ids_count": len(qdrant_chunk_ids),
            "unmapped_point_ids": (unmapped_point_ids[:DETAIL_LIMIT]),
            "missing_in_qdrant": (missing_in_qdrant[:DETAIL_LIMIT]),
            "missing_in_qdrant_count": len(missing_in_qdrant),
            "extra_in_qdrant": (extra_in_qdrant[:DETAIL_LIMIT]),
            "extra_in_qdrant_count": len(extra_in_qdrant),
            "error": None,
        }

    except Exception as error:
        return {
            "available": False,
            "collection_exists": None,
            "collection_name": collection_name,
            "points_count": None,
            "mapped_chunk_ids_count": 0,
            "unmapped_point_ids": [],
            "missing_in_qdrant": [],
            "extra_in_qdrant": [],
            "error": f"{type(error).__name__}: {error}",
        }

    finally:
        close_method = getattr(client, "close", None)

        if callable(close_method):
            close_method()


def build_issue_list(
    postgres_report: dict[str, Any],
    qdrant_report: dict[str, Any],
) -> list[str]:
    """Формирует список обнаруженных проблем."""
    issues = []

    if postgres_report["document_count"] == 0:
        issues.append("PostgreSQL не содержит документов.")

    if postgres_report["chunk_count"] == 0:
        issues.append("PostgreSQL не содержит чанков.")

    documents_without_chunks = postgres_report["documents_without_chunks"]["count"]

    if documents_without_chunks:
        issues.append(f"Обнаружены документы без чанков: {documents_without_chunks}.")

    duplicate_checksums = postgres_report["duplicates"]["checksum"]

    if duplicate_checksums:
        issues.append(
            "Обнаружены группы документов с одинаковым checksum: "
            f"{len(duplicate_checksums)}."
        )

    duplicate_external_ids = postgres_report["duplicates"]["external_id"]

    if duplicate_external_ids:
        issues.append(
            f"Обнаружены повторяющиеся external_id: {len(duplicate_external_ids)}."
        )

    legacy_source_types = postgres_report["legacy_source_types"]

    if legacy_source_types:
        issues.append(f"Остались устаревшие source_type: {legacy_source_types}.")

    missing_required_metadata = postgres_report["missing_required_metadata"]

    for field_name, field_report in sorted(
        missing_required_metadata.items(),
    ):
        missing_count = field_report["count"]

        if missing_count:
            issues.append(
                "Не заполнено обязательное поле "
                f"{field_name}: {missing_count} документов."
            )

    if not qdrant_report["available"]:
        issues.append("Не удалось подключиться к Qdrant.")
    elif not qdrant_report["collection_exists"]:
        issues.append("Коллекция Qdrant не существует.")
    else:
        missing_count = qdrant_report.get(
            "missing_in_qdrant_count",
            0,
        )
        extra_count = qdrant_report.get(
            "extra_in_qdrant_count",
            0,
        )

        if missing_count:
            issues.append(f"Чанки PostgreSQL отсутствуют в Qdrant: {missing_count}.")

        if extra_count:
            issues.append(f"В Qdrant есть лишние точки: {extra_count}.")

        unmapped_count = len(qdrant_report["unmapped_point_ids"])

        if unmapped_count:
            issues.append(
                f"Не удалось определить chunk_id для точек Qdrant: {unmapped_count}."
            )

    return issues


def print_report_summary(report: dict[str, Any]) -> None:
    """Печатает краткий отчёт в консоль."""
    postgres_report = report["postgres"]
    qdrant_report = report["qdrant"]

    print()
    print("IRIS corpus audit")
    print("=================")
    print(f"Status: {report['status']}")
    print(f"PostgreSQL documents: {postgres_report['document_count']}")
    print(f"PostgreSQL chunks: {postgres_report['chunk_count']}")
    print(
        "Documents without chunks: "
        f"{postgres_report['documents_without_chunks']['count']}"
    )
    print(
        f"Duplicate checksum groups: {len(postgres_report['duplicates']['checksum'])}"
    )
    print(f"Legacy source types: {postgres_report['legacy_source_types']}")
    missing_required_count = sum(
        field_report["count"]
        for field_report in postgres_report["missing_required_metadata"].values()
    )
    print(f"Missing required metadata values: {missing_required_count}")
    print(f"Qdrant available: {qdrant_report['available']}")
    print(f"Qdrant collection exists: {qdrant_report['collection_exists']}")
    print(f"Qdrant points: {qdrant_report['points_count']}")

    if qdrant_report.get("missing_in_qdrant_count") is not None:
        print(f"Missing in Qdrant: {qdrant_report['missing_in_qdrant_count']}")

    if qdrant_report.get("extra_in_qdrant_count") is not None:
        print(f"Extra in Qdrant: {qdrant_report['extra_in_qdrant_count']}")

    if qdrant_report["error"]:
        print(f"Qdrant error: {qdrant_report['error']}")

    print()
    print("Issues:")

    if report["issues"]:
        for issue in report["issues"]:
            print(f"- {issue}")
    else:
        print("- No structural issues found.")

    print()
    print(f"Full report: {OUTPUT_PATH.as_posix()}")


def main() -> None:
    """Запускает аудит корпуса."""
    with SessionLocal() as session:
        postgres_report, database_chunk_ids = collect_postgres_report(session)

    qdrant_report = collect_qdrant_report(
        database_chunk_ids,
    )

    issues = build_issue_list(
        postgres_report,
        qdrant_report,
    )

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "needs_attention" if issues else "ok",
        "postgres": postgres_report,
        "qdrant": qdrant_report,
        "issues": issues,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print_report_summary(report)


if __name__ == "__main__":
    main()
