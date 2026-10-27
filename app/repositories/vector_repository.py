from typing import Protocol

from app.models.document import DocumentChunk
from app.models.retrieval import RetrievalResult, SearchRequest


class VectorRepositories(Protocol):
    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        ... 

    def search(
        self,
        request: SearchRequest
    ) -> list[RetrievalResult]:
        ...

    def delete_document_chunks(
        self,
        tenant_id:str,
        document_id: str,
    ) -> None:
        ...

    def health_check(
        self
    ) -> bool:
        ...