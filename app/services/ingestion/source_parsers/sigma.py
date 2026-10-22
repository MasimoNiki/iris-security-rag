from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.services.ingestion.source_parsers.common import (
    build_markdown_document,
    format_list,
    format_yaml_block,
)


def load_sigma_rule(file_path: Path) -> dict[str, Any]:
    """Load and minimally validate a Sigma detection rule."""
    with file_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise TypeError(f"Invalid Sigma rule format: {file_path}")

    if not data.get("id") or not data.get("title"):
        raise ValueError(f"Sigma rule is missing id or title: {file_path}")

    return data


def normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        raw_values = value
    else:
        raw_values = [value]

    return [str(item).strip() for item in raw_values if str(item).strip()]


def sigma_rule_to_markdown(
    rule: dict[str, Any],
    *,
    repository_revision: str,
    upstream_path: str,
) -> str:
    """Convert an official Sigma rule to ingestion-ready Markdown."""
    title = str(rule["title"]).strip()
    rule_id = str(rule["id"]).strip()
    tags = normalize_string_list(rule.get("tags"))
    logsource = rule.get("logsource") or {}
    detection = rule.get("detection") or {}
    false_positives = normalize_string_list(rule.get("falsepositives"))
    references = normalize_string_list(rule.get("references"))
    modified = rule.get("modified")
    created = rule.get("date")
    rule_revision = str(modified or created or "unknown")
    source_revision = f"{rule_revision}@{repository_revision[:12]}"
    source_url = (
        f"https://github.com/SigmaHQ/sigma/blob/{repository_revision}/{upstream_path}"
    )
    metadata = {
        "title": title,
        "source_type": "sigma_rule",
        "external_id": rule_id,
        "source_url": source_url,
        "source_revision": source_revision,
        "language": "en",
        "domain": "detection_engineering",
        "tags": ["sigma", *tags],
        "repository": "SigmaHQ/sigma",
        "repository_revision": repository_revision,
        "upstream_path": upstream_path,
        "status": rule.get("status"),
        "level": rule.get("level"),
        "author": rule.get("author"),
        "date": created,
        "modified": modified,
        "related": rule.get("related") or [],
        "logsource": logsource,
    }
    description = str(
        rule.get("description") or "No description provided.",
    ).strip()
    body = f"""
# {title}

## Summary

{description}

## Rule metadata

- Rule ID: {rule_id}
- Status: {rule.get("status") or "Not specified"}
- Level: {rule.get("level") or "Not specified"}
- Author: {rule.get("author") or "Not specified"}
- Created: {created or "Not specified"}
- Modified: {modified or "Not specified"}
- Upstream path: {upstream_path}

## Log source

{format_yaml_block(logsource)}

## Detection logic

{format_yaml_block(detection)}

## False positives

{format_list(false_positives)}

## References

{format_list(references)}

## ATT&CK and Sigma tags

{format_list(tags)}
"""

    return build_markdown_document(metadata, body)


def convert_sigma_file_to_markdown(
    source_path: Path,
    output_path: Path | None = None,
    *,
    repository_revision: str = "local",
    upstream_path: str | None = None,
    output_dir: Path | None = None,
) -> Path:
    """Convert a rule while preserving the previous output_dir API."""
    if output_path is not None and output_dir is not None:
        raise ValueError(
            "Pass either output_path or output_dir, not both.",
        )

    if output_path is None:
        if output_dir is None:
            raise ValueError("output_path or output_dir is required.")

        output_path = output_dir / f"{source_path.stem}.md"

    if upstream_path is None:
        upstream_path = source_path.as_posix()

    rule = load_sigma_rule(source_path)
    markdown = sigma_rule_to_markdown(
        rule,
        repository_revision=repository_revision,
        upstream_path=upstream_path,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    return output_path
