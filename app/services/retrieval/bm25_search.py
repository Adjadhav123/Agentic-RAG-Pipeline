import re 

from rank_bm25 import BM25Okapi

from app.models.document import DocumentRecord
from app.models.retrieval import RetrievalResult, SearchRequest
from app.repositories.sql_document_repositories import SQLDocumentRepository
from app.utils.text import split_document

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+(?:[-_/][a-zA-Z0-9]+)*")

def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


class BM25Search:
    def __init__(
        self,
        document_repository: SQLDocumentRepository | None = None,
    ) -> None:
        self.document_repository = (
            document_repository or SQLDocumentRepository()
        )

    def _load_tenant_document(
        self, 
        tenant_id: str,
    ) -> list[DocumentRecord]:
        """Load all documents records for a tenant."""

        documents: list[DocumentRecord] = []
        offset = 0 
        page_size = 500

        while True:
            page = self.document_repository.list_documents(
                tenant_id,
                limit=page_size,
                offset=offset,
            )

            documents.extend(page)

            if len(page) < page_size:
                break

            offset +=   page_size

        return documents


    def search(
        self,
        request: SearchRequest,
    ) -> list[RetrievalResult]:
        if not request.query.strip():
            raise ValueError("Search Query cannot be empty")
        if not request.tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")  

        if not 1 <= request.top_k <=100:
            raise ValueError("top_k must be between 1 and 100")

        documents = self._load_tenant_document(request.tenant_id)

        candidate_chunks = []
        tokenized_chunks: list[list[str]] = []

        for document in documents:
            for chunk in split_document(document):
                metadata = {
                    **chunk.metadata,
                    "chunk_id": chunk.chunk_id,
                    "tenant_id": chunk.tenant_id,
                    "document_id": chunk.document_id,
                    "source": chunk.source,
                    "chunk_index": chunk.chunk_index,
                    "start_index": chunk.start_index,
                    "content_hash": chunk.content_hash,
                }

                if any(
                    metadata.get(key) != value
                    for key, value in request.filters.items()
                    if key not in {"tenant_id", "chunk_id"}
                ):
                    continue 

                tokens = tokenize(chunk.content)

                if not tokens:
                    continue

                candidate_chunks.append((chunk, metadata))
                tokenized_chunks.append(tokens)

        if not candidate_chunks:
            return []

        query_tokens = tokenize(request.query)
        if not query_tokens:
            return []

        bm25 = BM25Okapi(tokenized_chunks)
        scores = bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: float(scores[index]),
            reverse=True,
        )[:request.top_k]


        results : list[RetrievalResult] = []

        for index in ranked_indices:
            chunk, metadata = candidate_chunks[index]
            score = float(scores[index])

            if score <= 0:
                continue 

            results.append(
                RetrievalResult(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    tenant_id=chunk.tenant_id,
                    source=chunk.source,
                    content=chunk.content,
                    method="bm25",
                    rank=len(results) + 1,
                    score=score,
                    metadata=metadata,
                )
            )


        return results
                

                


                


