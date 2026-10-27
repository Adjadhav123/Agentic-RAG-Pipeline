from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.core.config import get_settings
from app.models.document import DocumentChunk
from app.models.retrieval import RetrievalResult, SearchRequest


def _build_filter(
    tenant_id: str,
    filters: dict[str, Any],
) -> dict[str, Any]:
    """Its purpose is to build a Chroma filter that always restricts searches to requested tentant."""

    clauses: list[dict[str, Any]] = [
        {"tenant_id": {"$eq": tenant_id}}
    ]

    for key, value in filters.items():
        if key in {
            "tenant_id",
            "chunk_id",
            "document_id"
        }:
            if key == "document_id":
                clauses.append({key:{"$eq": value}})
            continue

        if isinstance(value, (str, int, float, bool)):
            clauses.append({key:{"$eq": value}})


    if len(clauses) == 1:
        return clauses[0]

    return {"$and": clauses}


class ChromaVectorRepository:
    def __init__(self, store:Chroma):
        self._store = store

    def upsert_chunks(
        self,
        chunks: list[DocumentChunk]
    ) -> None:

        if not chunks:
            return None

        ids = [chunk.chunk_id for chunk in chunks]

        documents = [
            Document(
                page_content=chunk.content,
                metadata=chunk.to_storage_metadata(),
            )
            for chunk in chunks
        ]

        self._store.add_documents(
            documents=documents,
            ids=ids,
        )


    def search(
        self,
        request: SearchRequest
    ) -> list[RetrievalResult]:
        if not request.query.strip():
            return []

        if not request.tenant_id:
            raise ValueError("tenant_id is required")

        if not 1 <= request.top_k <= 100:
            raise ValueError("top_k must be between 1 and 100")

        where = _build_filter(
            request.tenant_id,
            request.filters
        )

        matches = self._store.similarity_search_with_score(
            query=request.query,
            k=request.top_k,
            filter=where
        )

        results: list[RetrievalResult] = []

        for rank, (document, distance) in enumerate(matches, start=1):
            metadata = dict(document.metadata)

            if metadata.get("tenant_id") != request.tenant_id:
                continue

            
            results.append(
                RetrievalResult(
                    chunk_id=str(metadata.get("chunk_id", "")),
                    document_id=str(metadata.get("document_id")),
                    tenant_id=request.tenant_id,
                    source=str(metadata.get("source")),
                    content=document.page_content,
                    method="vector",
                    rank=rank,
                    score=float(distance),
                    metadata=metadata,
                )
            )

        
        return results

    def delete_document_chunks(
        self,
        tenant_id: str,
        document_id: str,
    ) -> None:
        
        self._store.delete(
            where={
                "$and":[
                    {"tenant_id": {"$eq": tenant_id}},
                    {"document_id": {"$eq": document_id}}
                ]
            }
        )

    def health_check(self) -> bool:
        try:
            self._store.get(limit=1)
            return True
        except Exception:
            return False

    
@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    settings = get_settings()

    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device":"cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

@lru_cache(maxsize=1)
def get_chroma_store() -> Chroma:
    settings = get_settings()
    Path(settings.chroma_dir).mkdir(
        parents=True,
        exist_ok=True,
    )

    return Chroma(
        collection_name=settings.chroma_collection,
        persist_directory=str(settings.chroma_dir),
        embedding_function=get_embedding_model()
    )

@lru_cache(maxsize=1)
def get_vector_repository() -> ChromaVectorRepository:
    return ChromaVectorRepository(get_chroma_store())