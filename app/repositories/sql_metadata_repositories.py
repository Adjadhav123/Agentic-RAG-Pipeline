from sqlalchemy import select

from app.infrastructure.database import DocumentMetadataORM, IngestionStatusORM, SessionLocal

class SQLMetadataRepositories:
    ALLOWED_STATUSES = {
        "pending",
        "processing",
        "indexed",
        "failed",
        "deleting"
    }

    def get_document_version(
        self,
        *,
        tenant_id: str,
        document_id: str
    ) -> int | None :
        with SessionLocal() as session:
            return session.scalar(
                select(DocumentMetadataORM.version).where(
                    DocumentMetadataORM.tenant_id == tenant_id,
                    DocumentMetadataORM.document_id == document_id,
                )
            )


    def mark_ingestion_status(
        self,
        *,
        tenant_id: str,
        document_id: str,
        status: str,
        error_message: str | None = None,
    ) -> None:
         if status not in self.ALLOWED_STATUSES:
            raise ValueError(f"Unsupported ingestion status: {status}")
        
         with SessionLocal.begin() as session:
            row = session.get(
                IngestionStatusORM,
                (tenant_id, document_id)
            )

            if row is None:
                row = IngestionStatusORM(
                    tenant_id=tenant_id,
                    document_id=document_id,
                    status=status,
                    error_message=error_message
                )
                session.add(row)

            else:
                row.status=status
                row.error_message=error_message


            


