from __future__ import annotations

import json
from pathlib import Path

from app.services.ingestion.metadata import (
    build_document_metadata,
    extract_front_matter,
)
from app.services.ingestion.source_parsers.mitre import (
    find_active_techniques,
    resolve_mitre_output_path,
    technique_to_markdown,
)
from app.services.ingestion.source_parsers.owasp import (
    owasp_document_to_markdown,
)
from app.services.ingestion.source_parsers.sigma import (
    convert_sigma_file_to_markdown,
    sigma_rule_to_markdown,
)


def parse_generated_markdown(
    markdown: str,
) -> tuple[dict[str, object], str]:
    metadata, body = extract_front_matter(markdown)
    return metadata, body


def test_metadata_parser_supports_nested_yaml() -> None:
    markdown = """---
title: Example
source_type: sigma_rule
external_id: rule-1
source_url: https://example.test/rule-1
source_revision: 2026-01-01@abcdef
language: en
domain: detection_engineering
tags:
  - sigma
  - attack.t1003
date: 2026-01-01
logsource:
  product: windows
---

# Example
"""
    front_matter, body = extract_front_matter(markdown)
    document_metadata = build_document_metadata(
        file_path=Path("data/raw/sources/sigma/example.md"),
        raw_text=markdown,
        front_matter=front_matter,
        body_text=body,
    )

    assert document_metadata.external_id == "rule-1"
    assert document_metadata.tags == ["sigma", "attack.t1003"]
    assert document_metadata.metadata_json["date"] == "2026-01-01"
    assert document_metadata.metadata_json["logsource"] == {
        "product": "windows",
    }
    json.dumps(document_metadata.metadata_json)


def test_mitre_converter_adds_required_metadata() -> None:
    technique = {
        "type": "attack-pattern",
        "id": "attack-pattern--example",
        "name": "OS Credential Dumping",
        "description": "Adversaries may dump credentials.",
        "modified": "2026-01-01T00:00:00.000Z",
        "x_mitre_version": "3.0",
        "x_mitre_platforms": ["Windows"],
        "x_mitre_permissions_required": ["Administrator"],
        "kill_chain_phases": [
            {
                "kill_chain_name": "mitre-attack",
                "phase_name": "credential-access",
            }
        ],
        "external_references": [
            {
                "source_name": "mitre-attack",
                "external_id": "T1003",
                "url": "https://attack.mitre.org/techniques/T1003/",
            }
        ],
    }
    indexed = find_active_techniques({"objects": [technique]})
    markdown = technique_to_markdown(
        indexed["T1003"],
        repository_revision="a" * 40,
        upstream_path="enterprise-attack/enterprise-attack.json",
    )
    metadata, body = parse_generated_markdown(markdown)

    assert metadata["source_type"] == "mitre_attack"
    assert metadata["external_id"] == "T1003"
    assert metadata["language"] == "en"
    assert metadata["domain"] == "enterprise_attack"
    assert metadata["source_revision"] == "3.0@aaaaaaaaaaaa"
    assert "Adversaries may dump credentials." in body


def test_mitre_parent_does_not_reuse_subtechnique_file(
    tmp_path: Path,
) -> None:
    subtechnique_path = tmp_path / "t1003_001_lsass_memory.md"
    parent_path = tmp_path / "credential_dumping_t1003.md"
    subtechnique_path.write_text("# Subtechnique\n", encoding="utf-8")
    parent_path.write_text("# Parent\n", encoding="utf-8")

    resolved = resolve_mitre_output_path(
        tmp_path,
        external_id="T1003",
        title="OS Credential Dumping",
    )

    assert resolved == parent_path


def test_sigma_converter_preserves_detection_structure() -> None:
    rule = {
        "title": "Suspicious LSASS Access",
        "id": "11111111-2222-3333-4444-555555555555",
        "status": "test",
        "description": "Detects suspicious access to LSASS.",
        "author": "Example",
        "date": "2025-01-01",
        "modified": "2026-01-01",
        "tags": ["attack.credential-access", "attack.t1003.001"],
        "logsource": {
            "category": "process_access",
            "product": "windows",
        },
        "detection": {
            "selection": {"TargetImage|endswith": "\\lsass.exe"},
            "condition": "selection",
        },
        "falsepositives": ["Administrative tools"],
        "level": "high",
    }
    markdown = sigma_rule_to_markdown(
        rule,
        repository_revision="b" * 40,
        upstream_path="rules/windows/example.yml",
    )
    metadata, body = parse_generated_markdown(markdown)

    assert metadata["source_type"] == "sigma_rule"
    assert metadata["external_id"] == rule["id"]
    assert metadata["source_revision"] == "2026-01-01@bbbbbbbbbbbb"
    assert metadata["logsource"]["product"] == "windows"
    assert "TargetImage|endswith" in body
    assert "\\lsass.exe" in body


def test_sigma_converter_keeps_output_dir_compatibility(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "example.yml"
    output_dir = tmp_path / "output"
    source_path.write_text(
        """title: Example
id: 11111111-2222-3333-4444-555555555555
description: Example rule
logsource:
  product: windows
detection:
  selection:
    Image: example.exe
  condition: selection
""",
        encoding="utf-8",
    )

    output_path = convert_sigma_file_to_markdown(
        source_path=source_path,
        output_dir=output_dir,
    )

    assert output_path == output_dir / "example.md"
    assert output_path.exists()


def test_owasp_converter_replaces_upstream_front_matter() -> None:
    upstream = """---
title: Broken Access Control
layout: col-sidebar
---

# A01:2025 Broken Access Control

Access control enforces policy.
"""
    markdown = owasp_document_to_markdown(
        upstream,
        filename="A01_2025-Broken_Access_Control.md",
        repository_revision="c" * 40,
        upstream_path=("2025/docs/en/A01_2025-Broken_Access_Control.md"),
    )
    metadata, body = parse_generated_markdown(markdown)

    assert metadata["source_type"] == "owasp_top10"
    assert metadata["external_id"] == "A01:2025"
    assert metadata["source_revision"] == "2025@cccccccccccc"
    assert metadata["upstream_metadata"]["layout"] == "col-sidebar"
    assert body.count("---") == 0
    assert "Access control enforces policy." in body
