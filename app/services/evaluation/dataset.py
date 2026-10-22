from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class GoldenQuestion:
    id: str
    question: str
    expected_source_keywords: list[str] = field(default_factory=list)
    expected_external_ids: list[str] = field(default_factory=list)
    expected_local_paths: list[str] = field(default_factory=list)
    language: str = "unknown"
    tags: list[str] = field(default_factory=list)
    min_keyword_matches: int = 1
    answerable: bool = True

    @property
    def has_document_expectation(self) -> bool:
        return bool(self.expected_external_ids or self.expected_local_paths)

    @property
    def has_content_expectation(self) -> bool:
        return bool(self.expected_source_keywords)


def _string_list(
    value: Any,
    *,
    field_name: str,
    question_id: str,
) -> list[str]:
    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(
            f"{question_id}: {field_name} must be a YAML list.",
        )

    result = [str(item).strip() for item in value if str(item).strip()]

    if len(result) != len(set(result)):
        raise ValueError(
            f"{question_id}: {field_name} contains duplicate values.",
        )

    return result


def _boolean(
    value: Any,
    *,
    field_name: str,
    question_id: str,
) -> bool:
    if isinstance(value, bool):
        return value

    raise ValueError(
        f"{question_id}: {field_name} must be true or false.",
    )


def _load_question(item: Any, index: int) -> GoldenQuestion:
    if not isinstance(item, dict):
        raise ValueError(
            f"Dataset item #{index} must be a YAML mapping.",
        )

    question_id = str(item.get("id", "")).strip()
    question_text = str(item.get("question", "")).strip()

    if not question_id:
        raise ValueError(f"Dataset item #{index} has no id.")

    if not question_text:
        raise ValueError(f"{question_id}: question must not be empty.")

    expected_keywords = _string_list(
        item.get("expected_source_keywords"),
        field_name="expected_source_keywords",
        question_id=question_id,
    )
    expected_external_ids = _string_list(
        item.get("expected_external_ids"),
        field_name="expected_external_ids",
        question_id=question_id,
    )
    expected_local_paths = _string_list(
        item.get("expected_local_paths"),
        field_name="expected_local_paths",
        question_id=question_id,
    )
    tags = _string_list(
        item.get("tags"),
        field_name="tags",
        question_id=question_id,
    )
    answerable = _boolean(
        item.get("answerable", True),
        field_name="answerable",
        question_id=question_id,
    )
    min_keyword_matches = int(item.get("min_keyword_matches", 1))

    if min_keyword_matches < 1:
        raise ValueError(
            f"{question_id}: min_keyword_matches must be at least 1.",
        )

    if expected_keywords and min_keyword_matches > len(expected_keywords):
        raise ValueError(
            f"{question_id}: min_keyword_matches exceeds the number "
            "of expected_source_keywords.",
        )

    has_document_expectation = bool(
        expected_external_ids or expected_local_paths,
    )

    if answerable and not (has_document_expectation or expected_keywords):
        raise ValueError(
            f"{question_id}: an answerable question must define a document "
            "expectation or expected_source_keywords.",
        )

    if not answerable and (has_document_expectation or expected_keywords):
        raise ValueError(
            f"{question_id}: an unanswerable question must not define "
            "expected documents or source keywords.",
        )

    return GoldenQuestion(
        id=question_id,
        question=question_text,
        expected_source_keywords=expected_keywords,
        expected_external_ids=expected_external_ids,
        expected_local_paths=expected_local_paths,
        language=str(item.get("language", "unknown")).strip() or "unknown",
        tags=tags,
        min_keyword_matches=min_keyword_matches,
        answerable=answerable,
    )


def load_golden_questions(dataset_path: Path) -> list[GoldenQuestion]:
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {dataset_path}",
        )

    with dataset_path.open("r", encoding="utf-8") as file:
        raw_items = yaml.safe_load(file)

    if not raw_items:
        raise ValueError(f"Evaluation dataset is empty: {dataset_path}")

    if not isinstance(raw_items, list):
        raise ValueError(
            f"Evaluation dataset must contain a YAML list: {dataset_path}",
        )

    questions = [
        _load_question(item, index) for index, item in enumerate(raw_items, start=1)
    ]
    question_ids = [question.id for question in questions]

    if len(question_ids) != len(set(question_ids)):
        duplicate_ids = sorted(
            question_id
            for question_id in set(question_ids)
            if question_ids.count(question_id) > 1
        )
        raise ValueError(
            "Evaluation dataset contains duplicate ids: " + ", ".join(duplicate_ids),
        )

    return questions
