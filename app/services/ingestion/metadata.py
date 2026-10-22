from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

FRONT_MATTER_PATTERN = re.compile(
    r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)",
    re.DOTALL,
)

SOURCE_TYPE_ALIASES = {
    "mitre": "mitre_attack",
    "mitre_summary": "mitre_attack",
    "owasp": "owasp_top10",
    "owasp_summary": "owasp_top10",
    "nist_summary": "nist",
    "synthetic_runbook": "runbook",
}


@dataclass
class DocumentMetadata:
    title: str
    source_type: str
    external_id: str | None
    source_url: str | None
    language: str | None
    domain: str | None
    tags: list[str]
    local_path: str
    checksum: str
    source_revision: str | None
    metadata_json: dict[str, Any]


def calculate_checksum(content: str) -> str:
    """Calculate a SHA-256 hash of the complete source document."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def normalize_json_value(value: Any) -> Any:
    """Convert YAML values to JSON-compatible values for JSONB."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, dict):
        return {str(key): normalize_json_value(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [normalize_json_value(item) for item in value]

    return str(value)


def extract_front_matter(
    markdown_text: str,
) -> tuple[dict[str, Any], str]:
    """Extract YAML front matter and return it with the Markdown body."""
    match = FRONT_MATTER_PATTERN.match(markdown_text)

    if match is None:
        return {}, markdown_text.strip()

    loaded_metadata = yaml.safe_load(match.group(1)) or {}

    if not isinstance(loaded_metadata, dict):
        raise TypeError("Markdown front matter must be a YAML mapping.")

    metadata = {
        str(key): normalize_json_value(value) for key, value in loaded_metadata.items()
    }
    body_text = markdown_text[match.end() :].strip()

    return metadata, body_text


def infer_title_from_text(text: str, fallback: str) -> str:
    """Use the first H1 heading or a filename-derived fallback."""
    for line in text.splitlines():
        stripped_line = line.strip()

        if stripped_line.startswith("# "):
            return stripped_line.removeprefix("# ").strip()

    return fallback


def normalize_optional_string(value: Any) -> str | None:
    """Normalize an optional metadata value to a non-empty string."""
    if value is None:
        return None

    normalized_value = str(value).strip()
    return normalized_value or None


def normalize_tags(value: Any) -> list[str]:
    """Normalize tags to a unique list of non-empty strings."""
    if value is None:
        return []

    if isinstance(value, str):
        raw_values = [value]
    elif isinstance(value, (list, tuple, set)):
        raw_values = list(value)
    else:
        raw_values = [value]

    tags: list[str] = []

    for raw_value in raw_values:
        tag = str(raw_value).strip()

        if tag and tag not in tags:
            tags.append(tag)

    return tags


def build_document_metadata(
    file_path: Path,
    raw_text: str,
    front_matter: dict[str, Any],
    body_text: str,
) -> DocumentMetadata:
    """Build normalized metadata used by the ingestion pipeline."""
    fallback_title = file_path.stem.replace("_", " ").replace("-", " ").title()
    title = normalize_optional_string(
        front_matter.get("title"),
    ) or infer_title_from_text(
        text=body_text,
        fallback=fallback_title,
    )

    raw_source_type = (
        normalize_optional_string(front_matter.get("source_type"))
        or file_path.parent.name
    )
    source_type = SOURCE_TYPE_ALIASES.get(
        raw_source_type,
        raw_source_type,
    )
    external_id = normalize_optional_string(
        front_matter.get("external_id"),
    )
    source_url = normalize_optional_string(
        front_matter.get("source_url"),
    )
    source_revision = normalize_optional_string(
        front_matter.get("source_revision"),
    )
    language = normalize_optional_string(
        front_matter.get("language"),
    )
    domain = normalize_optional_string(
        front_matter.get("domain"),
    )
    tags = normalize_tags(front_matter.get("tags"))

    known_fields = {
        "title",
        "source_type",
        "external_id",
        "source_url",
        "source_revision",
        "language",
        "domain",
        "tags",
    }
    extra_metadata = {
        key: normalize_json_value(value)
        for key, value in front_matter.items()
        if key not in known_fields
    }

    return DocumentMetadata(
        title=title,
        source_type=source_type,
        external_id=external_id,
        source_url=source_url,
        language=language,
        domain=domain,
        tags=tags,
        local_path=file_path.as_posix(),
        checksum=calculate_checksum(raw_text),
        source_revision=source_revision,
        metadata_json={
            "tags": tags,
            **extra_metadata,
        },
    )
