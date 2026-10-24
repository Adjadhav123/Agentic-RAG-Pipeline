from asyncio import streams
from typing import Protocol

from app.models.document import DocumentRecord


class DocumentRepositories(Protocol):
    def upsert_document(
        self,
        document: DocumentRecord,
    ) -> None:
        """Insert or update a document metadata record"""


    def get_document(
        self,
        tenant_id: str,
        document_id: str,
    ) -> DocumentRecord | None :
        ...

    def delete_document(
        self,
        tenant_id: str,
        document_id: str ,
    ) -> None:
        ... 

    def list_documents(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DocumentRecord]:
        ...
        