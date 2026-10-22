from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.services.ingestion.source_parsers.common import (
    build_markdown_document,
    format_list,
)

MITRE_REFERENCE_NAME = "mitre-attack"


def load_attack_bundle(file_path: Path) -> dict[str, Any]:
    """Load and minimally validate an ATT&CK STIX bundle."""
    data = json.loads(file_path.read_text(encoding="utf-8"))

    if not isinstance(data, dict) or not isinstance(data.get("objects"), list):
        raise TypeError(f"Invalid ATT&CK STIX bundle: {file_path}")

    return data


def get_attack_reference(
    stix_object: dict[str, Any],
) -> dict[str, Any] | None:
    """Return the canonical MITRE ATT&CK external reference."""
    for reference in stix_object.get("external_references") or []:
        if reference.get("source_name") == MITRE_REFERENCE_NAME:
            return reference

    return None


def get_external_id(stix_object: dict[str, Any]) -> str | None:
    reference = get_attack_reference(stix_object)

    if reference is None:
        return None

    external_id = reference.get("external_id")
    return str(external_id).strip() if external_id else None


def find_active_techniques(
    bundle: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Index active Enterprise ATT&CK techniques by external ID."""
    techniques: dict[str, dict[str, Any]] = {}

    for stix_object in bundle["objects"]:
        if stix_object.get("type") != "attack-pattern":
            continue

        if stix_object.get("revoked") or stix_object.get("x_mitre_deprecated"):
            continue

        external_id = get_external_id(stix_object)

        if external_id:
            techniques[external_id] = stix_object

    return techniques


def technique_tactics(technique: dict[str, Any]) -> list[str]:
    """Return ATT&CK tactic phase names."""
    tactics = {
        str(phase.get("phase_name", "")).strip()
        for phase in technique.get("kill_chain_phases") or []
        if phase.get("phase_name")
    }
    return sorted(tactics)


def technique_to_markdown(
    technique: dict[str, Any],
    *,
    repository_revision: str,
    upstream_path: str,
) -> str:
    """Convert one official ATT&CK technique to ingestion-ready Markdown."""
    external_id = get_external_id(technique)

    if external_id is None:
        raise ValueError("ATT&CK technique has no MITRE external ID.")

    reference = get_attack_reference(technique) or {}
    title = str(technique.get("name") or external_id)
    source_url = reference.get("url") or (
        f"https://attack.mitre.org/techniques/{external_id.replace('.', '/')}/"
    )
    tactics = technique_tactics(technique)
    platforms = sorted(str(value) for value in technique.get("x_mitre_platforms") or [])
    permissions_required = sorted(
        str(value) for value in technique.get("x_mitre_permissions_required") or []
    )
    data_sources = sorted(
        str(value) for value in technique.get("x_mitre_data_sources") or []
    )
    technique_version = str(technique.get("x_mitre_version") or "unknown")
    source_revision = f"{technique_version}@{repository_revision[:12]}"
    tags = [
        "mitre_attack",
        external_id.lower(),
        *(f"attack.{tactic}" for tactic in tactics),
    ]
    metadata = {
        "title": f"{external_id} — {title}",
        "source_type": "mitre_attack",
        "external_id": external_id,
        "source_url": source_url,
        "source_revision": source_revision,
        "language": "en",
        "domain": "enterprise_attack",
        "tags": tags,
        "repository": "mitre-attack/attack-stix-data",
        "repository_revision": repository_revision,
        "upstream_path": upstream_path,
        "stix_id": technique.get("id"),
        "stix_modified": technique.get("modified"),
        "technique_version": technique_version,
        "is_subtechnique": bool(
            technique.get("x_mitre_is_subtechnique"),
        ),
        "tactics": tactics,
        "platforms": platforms,
        "permissions_required": permissions_required,
        "data_sources": data_sources,
    }
    description = str(
        technique.get("description") or "No description provided.",
    ).strip()
    detection = str(technique.get("x_mitre_detection") or "").strip()
    detection_section = (
        detection
        if detection
        else "Detection guidance is not present in this technique object."
    )
    body = f"""
# {external_id} — {title}

## Description

{description}

## ATT&CK tactics

{format_list(tactics)}

## Platforms

{format_list(platforms)}

## Permissions required

{format_list(permissions_required)}

## Data sources

{format_list(data_sources)}

## Detection

{detection_section}

## Source

- Official ATT&CK page: {source_url}
- STIX object: {technique.get("id", "Not specified")}
- ATT&CK object version: {technique_version}
"""

    return build_markdown_document(metadata, body)


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower())
    return normalized.strip("_")


def resolve_mitre_output_path(
    output_dir: Path,
    *,
    external_id: str,
    title: str,
) -> Path:
    """Reuse an existing technique file when its name already contains the ID."""
    normalized_id = external_id.lower().replace(".", "_")
    external_id_pattern = re.compile(
        rf"^external_id:\s*[\"']?{re.escape(external_id)}[\"']?\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

    for candidate in sorted(output_dir.glob("*.md")):
        existing_text = candidate.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        if external_id_pattern.search(existing_text):
            return candidate

    if "." in external_id:
        filename_pattern = re.compile(
            rf"(?:^|_){re.escape(normalized_id)}(?:_|$)",
        )
    else:
        filename_pattern = re.compile(
            rf"(?:^|_){re.escape(normalized_id)}"
            r"(?!_\d{3})(?:_|$)",
        )

    for candidate in sorted(output_dir.glob("*.md")):
        normalized_name = candidate.stem.lower().replace(".", "_")

        if filename_pattern.search(normalized_name):
            return candidate

    return output_dir / f"{normalized_id}_{slugify(title)}.md"
