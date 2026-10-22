from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml


def to_json_compatible(value: Any) -> Any:
    """Convert parser values to types accepted by JSON and PostgreSQL JSONB."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, Path):
        return value.as_posix()

    if isinstance(value, dict):
        return {str(key): to_json_compatible(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [to_json_compatible(item) for item in value]

    return str(value)


def build_markdown_document(
    metadata: dict[str, Any],
    body: str,
) -> str:
    """Build Markdown with safe YAML front matter."""
    normalized_metadata = to_json_compatible(metadata)
    front_matter = yaml.safe_dump(
        normalized_metadata,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).strip()

    return f"---\n{front_matter}\n---\n\n{body.strip()}\n"


def format_list(values: list[str] | None) -> str:
    """Format a list as Markdown bullets."""
    if not values:
        return "- Not specified"

    return "\n".join(f"- {value}" for value in values)


def format_yaml_block(value: Any) -> str:
    """Format nested source data without losing its structure."""
    rendered = yaml.safe_dump(
        to_json_compatible(value),
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).strip()

    return f"```yaml\n{rendered}\n```"
