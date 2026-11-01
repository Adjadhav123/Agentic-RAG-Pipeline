import sys
from pathlib import Path

from app.core.config import get_settings
from app.infrastructure.database import init_database
from app.services.ingestion_service import IngestionService


def ingest_all(tenant_id: str = "default-tenant") -> None:
    settings = get_settings()
    init_database()

    docs_dir = Path(settings.documents_dir)
    if not docs_dir.exists():
        print(f"Directory {docs_dir} does not exist.")
        return

    service = IngestionService()
    files = list(docs_dir.glob("*.md")) + list(docs_dir.glob("*.txt"))

    if not files:
        print(f"No .md or .txt files found in {docs_dir}.")
        return

    succeeded = 0
    failed = 0

    print(f"Found {len(files)} document(s) in {docs_dir} for tenant '{tenant_id}':\n")

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")
            result = service.ingest_text(
                tenant_id=tenant_id,
                source=file_path.name,
                content=content,
                metadata={"filename": file_path.name},
            )
            status_tag = f"[{result['status'].upper()}]"
            print(
                f"{status_tag} {file_path.name} | chunks={result['chunks_indexed']} | unchanged={result['unchanged']}"
            )
            succeeded += 1
        except Exception as e:
            print(f"[FAILED] {file_path.name}: {e}")
            failed += 1

    print("\n--- Ingestion Summary ---")
    print(f"Total: {len(files)} | Succeeded: {succeeded} | Failed: {failed}")


if __name__ == "__main__":
    tenant = sys.argv[1] if len(sys.argv) > 1 else "default-tenant"
    ingest_all(tenant_id=tenant)

