from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document
from app.db.session import SessionLocal

SOURCE_TYPE_ALIASES = {
    "mitre": "mitre_attack",
    "mitre_summary": "mitre_attack",
    "nist_summary": "nist",
    "owasp": "owasp_top10",
    "owasp_summary": "owasp_top10",
    "synthetic_runbook": "runbook",
}


def normalize_source_type(source_type: str | None) -> str | None:
    """Возвращает каноническое значение source_type."""
    if source_type is None:
        return None

    normalized_value = source_type.strip()

    return SOURCE_TYPE_ALIASES.get(
        normalized_value,
        normalized_value,
    )


def find_documents_to_update(
    documents: list[Document],
) -> list[tuple[Document, str]]:
    """Находит документы с устаревшим source_type."""
    documents_to_update = []

    for document in documents:
        normalized_source_type = normalize_source_type(
            document.source_type,
        )

        if normalized_source_type is None:
            continue

        if normalized_source_type == document.source_type:
            continue

        documents_to_update.append((document, normalized_source_type))

    return documents_to_update


def find_external_id_conflicts(
    documents: list[Document],
) -> list[dict[str, Any]]:
    """
    Проверяет конфликты уникальной пары source_type + external_id.

    Конфликт может появиться, если старое и новое значения
    source_type после нормализации станут одинаковыми.
    """
    groups: defaultdict[
        tuple[str, str],
        list[Document],
    ] = defaultdict(list)

    for document in documents:
        normalized_source_type = normalize_source_type(
            document.source_type,
        )
        external_id = document.external_id

        if normalized_source_type is None:
            continue

        if external_id is None or not external_id.strip():
            continue

        group_key = (
            normalized_source_type,
            external_id.strip(),
        )
        groups[group_key].append(document)

    conflicts = []

    for (
        source_type,
        external_id,
    ), grouped_documents in groups.items():
        if len(grouped_documents) < 2:
            continue

        conflicts.append(
            {
                "source_type": source_type,
                "external_id": external_id,
                "documents": [
                    {
                        "id": document.id,
                        "title": document.title,
                        "current_source_type": document.source_type,
                        "local_path": document.local_path,
                    }
                    for document in grouped_documents
                ],
            }
        )

    return conflicts


def print_conflicts(
    conflicts: list[dict[str, Any]],
) -> None:
    """Выводит найденные конфликты."""
    print()
    print("External ID conflicts")
    print("=====================")

    for conflict in conflicts:
        print()
        print(f"{conflict['source_type']}:{conflict['external_id']}")

        for document in conflict["documents"]:
            print(
                f"  document_id={document['id']}, "
                f"source_type={document['current_source_type']}, "
                f"title={document['title']}"
            )


def normalize_documents(
    session: Session,
    apply_changes: bool,
) -> int:
    """Проверяет и при необходимости обновляет source_type."""
    documents = list(session.scalars(select(Document).order_by(Document.id)).all())

    conflicts = find_external_id_conflicts(documents)

    if conflicts:
        print_conflicts(conflicts)
        print()
        print(
            "Normalization stopped because it would create "
            "duplicate source_type + external_id pairs."
        )
        return 1

    documents_to_update = find_documents_to_update(
        documents,
    )

    current_counts = Counter(
        document.source_type or "<missing>" for document in documents
    )
    update_counts = Counter(
        (
            document.source_type or "<missing>",
            normalized_source_type,
        )
        for document, normalized_source_type in documents_to_update
    )

    print()
    print("IRIS source_type normalization")
    print("==============================")
    print(f"Mode: {'apply' if apply_changes else 'dry-run'}")
    print(f"Documents checked: {len(documents)}")
    print(f"Documents requiring update: {len(documents_to_update)}")

    print()
    print("Current source types:")

    for source_type, count in sorted(current_counts.items()):
        print(f"- {source_type}: {count}")

    print()
    print("Planned changes:")

    if not update_counts:
        print("- No changes required.")
        return 0

    for (
        current_source_type,
        normalized_source_type,
    ), count in sorted(update_counts.items()):
        print(f"- {current_source_type} -> {normalized_source_type}: {count}")

    print()
    print("Affected documents:")

    for document, normalized_source_type in documents_to_update:
        print(
            f"- id={document.id}: "
            f"{document.source_type} -> "
            f"{normalized_source_type}; "
            f"title={document.title}"
        )

    if not apply_changes:
        session.rollback()
        print()
        print("Dry-run completed. No database changes were made.")
        print("Run again with --apply to save these changes.")
        return 0

    for document, normalized_source_type in documents_to_update:
        document.source_type = normalized_source_type

    session.commit()

    print()
    print(f"Normalization completed. Updated documents: {len(documents_to_update)}")

    return 0


def parse_arguments() -> argparse.Namespace:
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description=("Normalize legacy Document.source_type values.")
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Save changes to PostgreSQL.",
    )

    return parser.parse_args()


def main() -> int:
    """Запускает нормализацию source_type."""
    arguments = parse_arguments()

    with SessionLocal() as session:
        return normalize_documents(
            session=session,
            apply_changes=arguments.apply,
        )


if __name__ == "__main__":
    raise SystemExit(main())
