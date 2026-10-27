import json 
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.infrastructure.database import (
    DocumentMetadataORM,
    SessionLocal
)

from app.models.document import DocumentRecord

class SQLDocumentRepository:
    def upsert_document(
        self,
        document: DocumentRecord
    ) -> None:
        with SessionLocal.begin() as session:
            row = session.get(
                DocumentMetadataORM,
                (document.document_id, document.tenant_id)
            )

            if row is None:
                row = DocumentMetadataORM(
                    document_id=document.document_id,
                    tenant_id=document.tenant_id,
                    source=document.source,
                    content_hash=document.content_hash,
                    content=document.content,
                    version=document.version,
                    metadata_json=json.dumps(document.metadata)
                )
                
                session.add(row)

            else:
                row.source = document.source
                row.content_hash = document.content_hash
                row.content = document.content
                row.version = document.version
                row.metadata_json = json.dumps(document.metadata)

    

    def get_document(
        self, 
        tenant_id: str,
        document_id: str
    ) -> DocumentRecord | None:
        with SessionLocal() as session:
            row = session.get(
                DocumentMetadataORM,
                (document_id, tenant_id)
            )

            return self._to_domain(row) if row else None 


    
    def delete_document(
        self,
        tenant_id: str,
        document_id: str,
    ) -> None:
        with SessionLocal.begin() as session:
            session.execute(
                delete(DocumentMetadataORM).where(
                    DocumentMetadataORM.document_id == document_id,
                    DocumentMetadataORM.tenant_id == tenant_id
                )
            )

    def list_documents(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
        offset: int = 0
    ) -> list[DocumentRecord]:
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 to 500.")
        if offset < 0:
            raise ValueError("Offset must be non negative")

        with SessionLocal() as session:
            rows = session.scalars(
                select(DocumentMetadataORM)
                .where(DocumentMetadataORM.tenant_id == tenant_id)
                .order_by(DocumentMetadataORM.source)
                .limit(limit)
                .offset(offset)
            ).all()

            return [self._to_domain(row) for row in rows]


    @staticmethod
    def _to_domain(row: DocumentMetadataORM) -> DocumentRecord:
        return DocumentRecord(
            document_id=row.document_id,
            tenant_id=row.tenant_id,
            source=row.source,
            content_hash=row.content_hash,
            content=row.content,
            version=row.version,
            metadata=json.loads(row.metadata_json),
            created_at=row.created_at or datetime.now().astimezone(),
        )
            

