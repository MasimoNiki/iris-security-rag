from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import cache
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from app.services.ingestion.source_parsers.mitre import (
    find_active_techniques,
    load_attack_bundle,
    resolve_mitre_output_path,
    technique_to_markdown,
)
from app.services.ingestion.source_parsers.owasp import (
    owasp_document_to_markdown,
    resolve_owasp_output_path,
)
from app.services.ingestion.source_parsers.sigma import (
    convert_sigma_file_to_markdown,
    load_sigma_rule,
)

MITRE_REPOSITORY = "mitre-attack/attack-stix-data"
SIGMA_REPOSITORY = "SigmaHQ/sigma"
OWASP_REPOSITORY = "OWASP/Top10"
DEFAULT_BRANCH = "master"

MITRE_BUNDLE_PATH = "enterprise-attack/enterprise-attack.json"

MITRE_TECHNIQUE_IDS = [
    "T1059.001",
    "T1566.001",
    "T1566.002",
    "T1204.002",
    "T1003",
    "T1003.001",
    "T1555",
    "T1552.001",
    "T1110",
    "T1087",
    "T1082",
    "T1057",
    "T1018",
    "T1021",
    "T1021.001",
    "T1021.002",
    "T1047",
    "T1569.002",
    "T1547.001",
    "T1053.005",
    "T1543.003",
    "T1105",
    "T1071.001",
    "T1095",
    "T1041",
    "T1560.001",
    "T1486",
    "T1490",
    "T1070.004",
    "T1218.010",
]

OWASP_FILENAMES = [
    "A01_2025-Broken_Access_Control.md",
    "A02_2025-Security_Misconfiguration.md",
    "A03_2025-Software_Supply_Chain_Failures.md",
    "A04_2025-Cryptographic_Failures.md",
    "A05_2025-Injection.md",
    "A06_2025-Insecure_Design.md",
    "A07_2025-Authentication_Failures.md",
    "A08_2025-Software_or_Data_Integrity_Failures.md",
    "A09_2025-Security_Logging_and_Alerting_Failures.md",
    "A10_2025-Mishandling_of_Exceptional_Conditions.md",
]

PREFERRED_SIGMA_FILENAMES = {
    "proc_creation_win_powershell_aadinternals_cmdlets_execution.yml",
    "proc_creation_win_office_outlook_susp_child_processes.yml",
    "proc_creation_win_office_outlook_enable_unsafe_client_mail_rules.yml",
    "proc_creation_win_regsvr32_flags_anomaly.yml",
    "proc_creation_win_dism_enable_powershell_web_access_feature.yml",
    "proc_creation_win_office_outlook_execution_from_temp.yml",
    "proc_creation_win_lsass_process_clone.yml",
    "proc_creation_win_regsvr32_http_ip_pattern.yml",
    "proc_creation_win_hktl_empire_powershell_launch.yml",
    "proc_creation_win_susp_lsass_dmp_cli_keywords.yml",
    "proc_creation_win_findstr_lsass.yml",
    "proc_creation_win_regsvr32_network_pattern.yml",
}

USER_AGENT = "IRIS-SOC-corpus-fetcher/1.0"


@dataclass(frozen=True)
class SigmaCandidate:
    source_path: Path
    upstream_path: str
    rule_id: str
    title: str
    tags: tuple[str, ...]
    status: str
    level: str


def build_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
    }
    github_token = os.getenv("GITHUB_TOKEN")

    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    return headers


def request_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers=build_headers(),
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()
    except urllib.error.URLError as error:
        raise RuntimeError(f"Failed to download {url}: {error}") from error


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = destination.with_suffix(
        f"{destination.suffix}.part",
    )
    request = urllib.request.Request(
        url,
        headers=build_headers(),
    )

    try:
        with (
            urllib.request.urlopen(request, timeout=120) as response,
            temporary_path.open("wb") as output_file,
        ):
            shutil.copyfileobj(response, output_file)
    except urllib.error.URLError as error:
        temporary_path.unlink(missing_ok=True)
        raise RuntimeError(f"Failed to download {url}: {error}") from error

    temporary_path.replace(destination)


def resolve_repository_revision(
    repository: str,
    branch: str = DEFAULT_BRANCH,
) -> str:
    url = f"https://api.github.com/repos/{repository}/commits/{branch}"

    try:
        data = json.loads(request_bytes(url))
    except RuntimeError:
        print(
            f"Warning: could not resolve {repository} commit; using branch {branch!r}.",
        )
        return branch

    revision = data.get("sha")

    if not isinstance(revision, str) or not revision.strip():
        print(
            f"Warning: invalid revision response for {repository}; "
            f"using branch {branch!r}.",
        )
        return branch

    return revision.strip()


def raw_github_url(
    repository: str,
    revision: str,
    path: str,
) -> str:
    return f"https://raw.githubusercontent.com/{repository}/{revision}/{path}"


@cache
def hash_file(file_path: Path) -> str:
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def relative_project_path(
    file_path: Path,
    project_root: Path,
) -> str:
    return file_path.relative_to(project_root).as_posix()


def build_manifest_document(
    *,
    project_root: Path,
    raw_path: Path,
    generated_path: Path,
    source_type: str,
    external_id: str,
    source_url: str,
    source_revision: str,
) -> dict[str, Any]:
    return {
        "source_type": source_type,
        "external_id": external_id,
        "source_url": source_url,
        "source_revision": source_revision,
        "raw_path": relative_project_path(raw_path, project_root),
        "raw_sha256": hash_file(raw_path),
        "generated_path": relative_project_path(
            generated_path,
            project_root,
        ),
        "generated_sha256": hash_file(generated_path),
    }


def fetch_mitre_documents(
    *,
    project_root: Path,
    revision: str,
) -> list[dict[str, Any]]:
    external_path = project_root / "data/external/mitre/enterprise-attack.json"
    output_dir = project_root / "data/raw/mitre"
    output_dir.mkdir(parents=True, exist_ok=True)
    source_url = raw_github_url(
        MITRE_REPOSITORY,
        revision,
        MITRE_BUNDLE_PATH,
    )
    print("Downloading MITRE ATT&CK Enterprise STIX bundle...")
    download_file(source_url, external_path)
    bundle = load_attack_bundle(external_path)
    techniques = find_active_techniques(bundle)
    missing_ids = [
        technique_id
        for technique_id in MITRE_TECHNIQUE_IDS
        if technique_id not in techniques
    ]

    if missing_ids:
        missing_text = ", ".join(missing_ids)
        raise RuntimeError(
            f"Selected active ATT&CK techniques were not found: {missing_text}",
        )

    manifest_documents: list[dict[str, Any]] = []

    for technique_id in MITRE_TECHNIQUE_IDS:
        technique = techniques[technique_id]
        output_path = resolve_mitre_output_path(
            output_dir,
            external_id=technique_id,
            title=str(technique.get("name") or technique_id),
        )
        markdown = technique_to_markdown(
            technique,
            repository_revision=revision,
            upstream_path=MITRE_BUNDLE_PATH,
        )
        output_path.write_text(markdown, encoding="utf-8")
        attack_reference = next(
            (
                reference
                for reference in technique.get("external_references") or []
                if reference.get("source_name") == "mitre-attack"
            ),
            {},
        )
        technique_url = attack_reference.get("url") or (
            f"https://attack.mitre.org/techniques/{technique_id.replace('.', '/')}/"
        )
        technique_version = str(
            technique.get("x_mitre_version") or "unknown",
        )
        manifest_documents.append(
            build_manifest_document(
                project_root=project_root,
                raw_path=external_path,
                generated_path=output_path,
                source_type="mitre_attack",
                external_id=technique_id,
                source_url=technique_url,
                source_revision=(f"{technique_version}@{revision[:12]}"),
            )
        )

    return manifest_documents


def sigma_sort_key(
    candidate: SigmaCandidate,
) -> tuple[int, int, int, str]:
    status_priority = {
        "stable": 0,
        "test": 1,
        "experimental": 2,
    }
    level_priority = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
        "informational": 4,
    }
    windows_priority = 0 if candidate.upstream_path.startswith("rules/windows/") else 1

    return (
        windows_priority,
        status_priority.get(candidate.status, 3),
        level_priority.get(candidate.level, 5),
        candidate.upstream_path,
    )


def load_sigma_candidates(
    repository_root: Path,
) -> tuple[list[SigmaCandidate], int]:
    rules_root = repository_root / "rules"

    if not rules_root.exists():
        raise FileNotFoundError(
            f"Sigma rules directory not found: {rules_root}",
        )

    candidates: list[SigmaCandidate] = []
    invalid_files = 0
    target_tags = {
        f"attack.{technique_id.lower()}" for technique_id in MITRE_TECHNIQUE_IDS
    }
    rule_files = sorted(rules_root.rglob("*.yml"))
    rule_files += sorted(rules_root.rglob("*.yaml"))

    for source_path in rule_files:
        try:
            rule = load_sigma_rule(source_path)
        except (OSError, TypeError, ValueError, yaml.YAMLError):
            invalid_files += 1
            continue

        status = str(rule.get("status") or "").strip().lower()

        if status in {"deprecated", "unsupported"}:
            continue

        tags = tuple(
            str(tag).strip().lower()
            for tag in rule.get("tags") or []
            if str(tag).strip()
        )

        if not target_tags.intersection(tags):
            continue

        candidates.append(
            SigmaCandidate(
                source_path=source_path,
                upstream_path=source_path.relative_to(
                    repository_root,
                ).as_posix(),
                rule_id=str(rule["id"]).strip(),
                title=str(rule["title"]).strip(),
                tags=tags,
                status=status,
                level=str(rule.get("level") or "").strip().lower(),
            )
        )

    candidates.sort(key=sigma_sort_key)
    return candidates, invalid_files


def select_sigma_candidates(
    candidates: list[SigmaCandidate],
    count: int,
) -> list[SigmaCandidate]:
    if count < 1:
        raise ValueError("Sigma rule count must be at least 1.")

    selected: list[SigmaCandidate] = []
    selected_ids: set[str] = set()

    def add_candidate(candidate: SigmaCandidate) -> bool:
        if candidate.rule_id in selected_ids:
            return False

        selected.append(candidate)
        selected_ids.add(candidate.rule_id)
        return True

    preferred_candidates = sorted(
        (
            candidate
            for candidate in candidates
            if candidate.source_path.name in PREFERRED_SIGMA_FILENAMES
        ),
        key=sigma_sort_key,
    )

    for candidate in preferred_candidates:
        add_candidate(candidate)

        if len(selected) == count:
            return selected

    candidates_by_tag: dict[str, list[SigmaCandidate]] = defaultdict(list)

    for candidate in candidates:
        for tag in candidate.tags:
            candidates_by_tag[tag].append(candidate)

    target_tags = [
        f"attack.{technique_id.lower()}" for technique_id in MITRE_TECHNIQUE_IDS
    ]
    indexes = {tag: 0 for tag in target_tags}

    while len(selected) < count:
        added_in_round = False

        for tag in target_tags:
            tagged_candidates = candidates_by_tag.get(tag, [])

            while indexes[tag] < len(tagged_candidates):
                candidate = tagged_candidates[indexes[tag]]
                indexes[tag] += 1

                if add_candidate(candidate):
                    added_in_round = True
                    break

            if len(selected) == count:
                return selected

        if not added_in_round:
            break

    for candidate in candidates:
        add_candidate(candidate)

        if len(selected) == count:
            return selected

    raise RuntimeError(
        f"Only {len(selected)} suitable Sigma rules were found; {count} requested.",
    )


def extract_sigma_rules(
    archive: zipfile.ZipFile,
    destination: Path,
) -> int:
    """Extract only Sigma detection rules using short, safe paths.

    The upstream archive also contains regression fixtures with paths that can
    exceed the legacy Windows MAX_PATH limit. The corpus builder only needs
    files below ``rules/``, so the repository's hash-prefixed root directory
    and every unrelated archive member are deliberately omitted.
    """
    extracted_count = 0

    for member in archive.infolist():
        if member.is_dir():
            continue

        archive_path = PurePosixPath(member.filename)
        path_parts = archive_path.parts

        if (
            len(path_parts) < 3
            or path_parts[1] != "rules"
            or archive_path.suffix.lower() not in {".yml", ".yaml"}
        ):
            continue

        relative_parts = path_parts[1:]

        if any(part in {"", ".", ".."} for part in relative_parts):
            raise RuntimeError(
                f"Unsafe path in Sigma archive: {member.filename}",
            )

        target_path = destination.joinpath(*relative_parts)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with archive.open(member) as source, target_path.open("wb") as target:
            shutil.copyfileobj(source, target)

        extracted_count += 1

    if extracted_count == 0:
        raise RuntimeError(
            "No rule files were found below rules/ in the Sigma archive.",
        )

    return extracted_count


def unique_sigma_output_path(
    output_dir: Path,
    candidate: SigmaCandidate,
    used_names: dict[str, str],
) -> Path:
    output_name = f"{candidate.source_path.stem}.md"
    existing_rule_id = used_names.get(output_name.lower())

    if existing_rule_id and existing_rule_id != candidate.rule_id:
        output_name = f"{candidate.source_path.stem}_{candidate.rule_id[:8]}.md"

    used_names[output_name.lower()] = candidate.rule_id
    return output_dir / output_name


def fetch_sigma_documents(
    *,
    project_root: Path,
    revision: str,
    count: int,
) -> tuple[list[dict[str, Any]], int]:
    output_dir = project_root / "data/raw/sources/sigma"
    external_dir = project_root / "data/external/sigma"
    output_dir.mkdir(parents=True, exist_ok=True)
    external_dir.mkdir(parents=True, exist_ok=True)
    archive_url = f"https://codeload.github.com/{SIGMA_REPOSITORY}/zip/{revision}"
    manifest_documents: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(
        prefix=".iris_sigma_",
        dir=project_root,
    ) as temporary_directory:
        temporary_dir = Path(temporary_directory)
        archive_path = temporary_dir / "sigma.zip"
        extracted_dir = temporary_dir / "extracted"
        extracted_dir.mkdir()
        print("Downloading SigmaHQ rule repository...")
        download_file(archive_url, archive_path)

        with zipfile.ZipFile(archive_path) as archive:
            extract_sigma_rules(archive, extracted_dir)

        repository_root = extracted_dir
        candidates, invalid_files = load_sigma_candidates(repository_root)
        selected = select_sigma_candidates(candidates, count)
        used_names: dict[str, str] = {}

        for candidate in selected:
            raw_path = external_dir / candidate.upstream_path
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate.source_path, raw_path)
            output_path = unique_sigma_output_path(
                output_dir,
                candidate,
                used_names,
            )
            convert_sigma_file_to_markdown(
                raw_path,
                output_path,
                repository_revision=revision,
                upstream_path=candidate.upstream_path,
            )
            rule = load_sigma_rule(raw_path)
            rule_revision = str(rule.get("modified") or rule.get("date") or "unknown")
            source_url = (
                "https://github.com/SigmaHQ/sigma/blob/"
                f"{revision}/{candidate.upstream_path}"
            )
            manifest_documents.append(
                build_manifest_document(
                    project_root=project_root,
                    raw_path=raw_path,
                    generated_path=output_path,
                    source_type="sigma_rule",
                    external_id=candidate.rule_id,
                    source_url=source_url,
                    source_revision=(f"{rule_revision}@{revision[:12]}"),
                )
            )

    return manifest_documents, invalid_files


def fetch_owasp_documents(
    *,
    project_root: Path,
    revision: str,
) -> list[dict[str, Any]]:
    external_dir = project_root / "data/external/owasp/2025"
    output_dir = project_root / "data/raw/owasp"
    external_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_documents: list[dict[str, Any]] = []
    print("Downloading OWASP Top 10:2025 pages...")

    for filename in OWASP_FILENAMES:
        upstream_path = f"2025/docs/en/{filename}"
        raw_path = external_dir / filename
        download_file(
            raw_github_url(
                OWASP_REPOSITORY,
                revision,
                upstream_path,
            ),
            raw_path,
        )
        content = raw_path.read_text(encoding="utf-8")
        category_id = filename[:3].upper()
        output_path = resolve_owasp_output_path(
            output_dir,
            category_id=category_id,
            canonical_filename=filename,
        )
        markdown = owasp_document_to_markdown(
            content,
            filename=filename,
            repository_revision=revision,
            upstream_path=upstream_path,
        )
        output_path.write_text(markdown, encoding="utf-8")
        source_url = f"https://github.com/OWASP/Top10/blob/{revision}/{upstream_path}"
        manifest_documents.append(
            build_manifest_document(
                project_root=project_root,
                raw_path=raw_path,
                generated_path=output_path,
                source_type="owasp_top10",
                external_id=f"{category_id}:2025",
                source_url=source_url,
                source_revision=f"2025@{revision[:12]}",
            )
        )

    return manifest_documents


def save_manifest(
    *,
    project_root: Path,
    revisions: dict[str, str],
    documents: list[dict[str, Any]],
    sigma_count: int,
    invalid_sigma_files: int,
) -> Path:
    manifest_path = project_root / "data/manifests/corpus_sources.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    source_counts: dict[str, int] = defaultdict(int)

    for document in documents:
        source_counts[document["source_type"]] += 1

    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "selection": {
            "mitre_technique_ids": MITRE_TECHNIQUE_IDS,
            "sigma_rule_count": sigma_count,
            "owasp_version": "2025",
        },
        "repositories": {
            "mitre_attack": {
                "repository": MITRE_REPOSITORY,
                "revision": revisions["mitre_attack"],
            },
            "sigma": {
                "repository": SIGMA_REPOSITORY,
                "revision": revisions["sigma"],
                "invalid_files_skipped": invalid_sigma_files,
            },
            "owasp": {
                "repository": OWASP_REPOSITORY,
                "revision": revisions["owasp"],
            },
        },
        "document_counts": dict(sorted(source_counts.items())),
        "documents": sorted(
            documents,
            key=lambda item: (
                item["source_type"],
                item["external_id"],
            ),
        ),
    }
    manifest_path.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return manifest_path


def print_plan(sigma_count: int) -> None:
    print("IRIS official corpus fetch plan")
    print("===============================")
    print(f"MITRE ATT&CK techniques: {len(MITRE_TECHNIQUE_IDS)}")
    print(f"SigmaHQ rules: {sigma_count}")
    print(f"OWASP Top 10:2025 pages: {len(OWASP_FILENAMES)}")
    print()
    print("Generated Markdown directories:")
    print("- data/raw/mitre")
    print("- data/raw/sources/sigma")
    print("- data/raw/owasp")
    print()
    print("No database or Qdrant changes are made by this script.")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download and normalize official MITRE ATT&CK, "
            "SigmaHQ, and OWASP Top 10 documents."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="IRIS project root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--sigma-count",
        type=int,
        default=60,
        help="Number of related Sigma rules to select.",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Print the planned corpus size without downloading files.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()

    if arguments.sigma_count < 1 or arguments.sigma_count > 500:
        raise ValueError("--sigma-count must be between 1 and 500.")

    if arguments.plan:
        print_plan(arguments.sigma_count)
        return 0

    project_root = arguments.project_root.resolve()

    if not (project_root / "pyproject.toml").exists():
        raise FileNotFoundError(
            "pyproject.toml was not found. Run this command from "
            "the IRIS project root.",
        )

    print("Resolving official repository revisions...")
    revisions = {
        "mitre_attack": resolve_repository_revision(MITRE_REPOSITORY),
        "sigma": resolve_repository_revision(SIGMA_REPOSITORY),
        "owasp": resolve_repository_revision(OWASP_REPOSITORY),
    }
    documents: list[dict[str, Any]] = []
    documents.extend(
        fetch_mitre_documents(
            project_root=project_root,
            revision=revisions["mitre_attack"],
        )
    )
    sigma_documents, invalid_sigma_files = fetch_sigma_documents(
        project_root=project_root,
        revision=revisions["sigma"],
        count=arguments.sigma_count,
    )
    documents.extend(sigma_documents)
    documents.extend(
        fetch_owasp_documents(
            project_root=project_root,
            revision=revisions["owasp"],
        )
    )
    manifest_path = save_manifest(
        project_root=project_root,
        revisions=revisions,
        documents=documents,
        sigma_count=arguments.sigma_count,
        invalid_sigma_files=invalid_sigma_files,
    )
    print()
    print("Official corpus preparation finished")
    print(f"MITRE ATT&CK documents: {len(MITRE_TECHNIQUE_IDS)}")
    print(f"SigmaHQ documents: {len(sigma_documents)}")
    print(f"OWASP Top 10 documents: {len(OWASP_FILENAMES)}")
    print(f"Total generated documents: {len(documents)}")
    print(f"Manifest: {relative_project_path(manifest_path, project_root)}")
    print()
    print("Next command: python scripts\\ingest_local_docs.py")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
