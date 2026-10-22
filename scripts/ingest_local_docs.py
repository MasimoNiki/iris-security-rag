from pathlib import Path

from app.db.session import SessionLocal
from app.services.ingestion.pipeline import ingest_local_documents


def main() -> None:
    raw_data_dir = Path("data/raw")

    if not raw_data_dir.exists():
        raise FileNotFoundError(f"Raw data directory not found: {raw_data_dir}")

    db = SessionLocal()

    try:
        result = ingest_local_documents(
            db=db,
            raw_data_dir=raw_data_dir,
        )

        print("Ingestion finished")
        print(f"Documents created: {result.documents_created}")
        print(f"Documents updated: {result.documents_updated}")
        print(f"Documents skipped: {result.documents_skipped}")
        print(f"Chunks created: {result.chunks_created}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
