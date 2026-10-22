from pathlib import Path

SUPPORTED_EXTENSIONS = {".md"}


def find_files(raw_data_dir: Path) -> list[Path]:
    files: list[Path] = []

    for file_path in raw_data_dir.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        files.append(file_path)

    return sorted(files)


def read_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")
