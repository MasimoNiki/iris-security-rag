from __future__ import annotations

from pathlib import Path

from app.services.ingestion.source_parsers.sigma import convert_sigma_file_to_markdown


def convert_sigma_sources() -> int:
    input_dir = Path("data/external/sigma")
    output_dir = Path("data/raw/sources/sigma")

    if not input_dir.exists():
        raise FileNotFoundError(f"Sigma input directory not found: {input_dir}")

    files = sorted(input_dir.rglob("*.yml"))
    files += sorted(input_dir.rglob("*.yaml"))

    converted = 0

    for file_path in files:
        convert_sigma_file_to_markdown(
            source_path=file_path,
            output_dir=output_dir,
        )
        converted += 1

    return converted


def main() -> None:
    sigma_converted = convert_sigma_sources()

    print("Source ingestion finished")
    print(f"Sigma rules converted: {sigma_converted}")
    print("Now run: python scripts\\ingest_local_docs.py")


if __name__ == "__main__":
    main()
