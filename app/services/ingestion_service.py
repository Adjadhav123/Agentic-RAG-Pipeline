from app.infrastructure.database import DocumentMetadataORM
import logging 
from dataclasses import replace
from typing import Any

from app.models.document import DocumentRecord
from app.models.retrieval import SearchRequest
from app.repositories.sql_metadata_repositories import SQLMetadataRepositories
from app.repositories.sql_document_repositories import SQLDocumentRepository
from app.infrastructure.vector_store import get_vector_repository
from app.utils.text import normalize_text, split_document
from app.core.logger import configure_logging

logger = configure_logging()


class IngestionService:
    def __init__(
        self,
        document_repository: SQLDocumentRepository | None = None,
        metadata_repository: SQLMetadataRepositories | None = None,
        vector_repositories: Any | None = None,
    ) -> None:
        self.document_repositories = (
            document_repository or SQLDocumentRepository()
        )

        self.metadata_repositories = (
            metadata_repository or SQLMetadataRepositories()
        )

        self.vector_repositories = (
            vector_repositories or get_vector_repository()
        )

    def ingest_text(
        self,
        *,
        tenant_id: str,
        source: str,
        content: str,
        metadata: dict[str, Any] | None = None
    ) ->dict[str, Any]:
        """Validate, chunk, store and index one text document."""

        tenant_id = tenant_id.strip()
        source = source.strip()
        content = normalize_text(content)

        if not tenant_id:
            raise ValueError("tenant_id cannot be empty")

        if not source:
            raise ValueError("Source cannot be empty")

        if not content:
            raise ValueError("Document content cannot be empty")

        metadata = metadata or {} 

        document = DocumentRecord.create(
            tenant_id=tenant_id,
            source=source,
            content=content,
            metadata=metadata
        )

        previous = self.document_repositories.get_document(
            tenant_id=tenant_id,
            document_id=document.document_id,
        )

        # Avoid the unnecessary embedding work for unchanged data. 
        if previous and previous.content_hash == document.content_hash:
            self.metadata_repositories.mark_ingestion_status(
                tenant_id=tenant_id,
                document_id=document.document_id,
                status="indexed",
            )

            return {
                "document_id": document.document_id,
                "status": "indexed",
                "chunks_indexed": 0,
                "unchanged": True,
                "message": "Document content has not changed."
            }

        version = previous.version + 1 if previous else 1
        document = replace(document, version=version)

        self.metadata_repositories.mark_ingestion_status(
            tenant_id=tenant_id,
            document_id=document.document_id,
            status="processing",
        )

        try:

            chunks = split_document(document)

            self.vector_repositories.upsert_chunks(chunks)

            self.document_repositories.upsert_document(document)

            self.metadata_repositories.mark_ingestion_status(
                tenant_id=tenant_id,
                document_id=document.document_id,
                status="indexed",
            )

            logger.info(
                f"Document indexed: tenant={tenant_id}, document={document.document_id}",
                tenant_id,
                document.document_id,
                len(chunks),
                document.version
            )

            return {
                "document_id": document.document_id,
                "status": "indexed",
                "chunks_indexed": len(chunks),
                "unchanged": False,
                "messaged": "Document ingested sucessfully."
            }

        except Exception as e:
            logger.exception(
                "Document ingestion failed: tenant=%s, document=%s",
                tenant_id,
                document.document_id
            )

            try:
                self.metadata_repositories.mark_ingestion_status(
                    tenant_id=tenant_id,
                    document_id=document.document_id,
                    status="failed",
                    error_message=str(e),
                )
            except Exception as e:
                logger.exception(
                    "Failed to mark ingestion as failed",
                    tenant_id=tenant_id,
                    document_id=document.document_id
                )

            raise




