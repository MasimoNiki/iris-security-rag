from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from app.services.ingestion.source_parsers.common import (
    build_markdown_document,
)

FRONT_MATTER_PATTERN = re.compile(
    r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)",
    re.DOTALL,
)
OWASP_FILENAME_PATTERN = re.compile(
    r"^(A\d{2})_2025-(.+)\.md$",
    re.IGNORECASE,
)


def split_upstream_markdown(
    content: str,
) -> tuple[dict[str, Any], str]:
    """Remove upstream front matter so IRIS can add normalized metadata."""
    match = FRONT_MATTER_PATTERN.match(content)

    if match is None:
        return {}, content.strip()

    loaded = yaml.safe_load(match.group(1)) or {}
    upstream_metadata = loaded if isinstance(loaded, dict) else {}
    body = content[match.end() :].strip()

    return upstream_metadata, body


def infer_title(body: str, fallback: str) -> str:
    for line in body.splitlines():
        stripped_line = line.strip()

        if stripped_line.startswith("# "):
            return stripped_line.removeprefix("# ").strip()

    return fallback


def owasp_document_to_markdown(
    content: str,
    *,
    filename: str,
    repository_revision: str,
    upstream_path: str,
) -> str:
    """Convert one official OWASP Top 10:2025 page to IRIS Markdown."""
    filename_match = OWASP_FILENAME_PATTERN.match(filename)

    if filename_match is None:
        raise ValueError(f"Unexpected OWASP Top 10 filename: {filename}")

    category_id = filename_match.group(1).upper()
    name_from_filename = filename_match.group(2).replace("_", " ").strip()
    upstream_metadata, body = split_upstream_markdown(content)
    title = infer_title(
        body,
        fallback=f"{category_id}:2025 {name_from_filename}",
    )
    external_id = f"{category_id}:2025"
    source_url = (
        f"https://github.com/OWASP/Top10/blob/{repository_revision}/{upstream_path}"
    )
    metadata = {
        "title": title,
        "source_type": "owasp_top10",
        "external_id": external_id,
        "source_url": source_url,
        "source_revision": f"2025@{repository_revision[:12]}",
        "language": "en",
        "domain": "application_security",
        "tags": [
            "owasp",
            "owasp_top10",
            external_id.lower(),
            "application_security",
        ],
        "repository": "OWASP/Top10",
        "repository_revision": repository_revision,
        "upstream_path": upstream_path,
        "owasp_version": "2025",
        "upstream_metadata": upstream_metadata,
    }

    return build_markdown_document(metadata, body)


def resolve_owasp_output_path(
    output_dir: Path,
    *,
    category_id: str,
    canonical_filename: str,
) -> Path:
    """Reuse legacy files so existing database documents are updated in place."""
    category_id = category_id.upper()

    if category_id == "A01":
        legacy_summary = output_dir / "broken_access_control.md"

        if legacy_summary.exists():
            return legacy_summary

    candidates = sorted(
        output_dir.glob(f"{category_id}_2025-*.md"),
    )

    if candidates:
        return candidates[0]

    return output_dir / canonical_filename
