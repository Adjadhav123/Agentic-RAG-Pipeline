from typing import Protocol

class MetadataRepository(Protocol):
    def get_document_version(
        self,
        *,
        tenant_id: str,
        document_id: str,
    ) -> int | None : 
        ...

    

    def mark_ingestion_status(
        self,
        *,
        tenant_id: str,
        document_id: str,
        status: str,
        error_message: str | None = None
    ) -> None :
        ...