from app.core.config import get_settings

from app.infrastructure.vector_store import get_vector_repository
from app.models.retrieval import RetrievalResult, SearchRequest
from app.repositories.vector_repository import VectorRepositories
from app.services.retrieval.bm25_search import BM25Search
from app.services.retrieval.reranker import CrossEncoderReranker
from app.services.retrieval.fusion import reciprocal_rank_fusion

class HybridSearchService:
    def __init__(
        self,
        *,
        vector_repository: VectorRepositories | None = None,
        bm25_search: BM25Search | None = None,
        reranker: CrossEncoderReranker | None = None,
    ) -> None:
        """Hybrid search service for combining vector and BM25 search results with reranking."""

        self.vector_repository = (
            vector_repository or get_vector_repository()
        )

        self.bm25_search = (
            bm25_search or BM25Search()
        )

        self.reranker = (
            reranker or CrossEncoderReranker()
        )

    def search(
        self,
        request: SearchRequest,
    ) -> list[RetrievalResult]:
        settings = get_settings()

        if not request.query.strip():
            raise ValueError("Search query cannot be empty")
        if not request.tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")
        if not 1 <= request.top_k <= 100:
            raise ValueError("top_k must be between 1 and 100")

        vector_results = self.vector_repository.search(request)
        bm25_results = self.bm25_search.search(request)

        fused_results = reciprocal_rank_fusion(
            [vector_results, bm25_results],
            rrf_k=60,
        )

        if not fused_results:
            return []

        final_k = min(request.top_k, settings.final_top_k)

        candidate_limit = min(
            len(fused_results),
            max(settings.retrieval_top_k, final_k)

        )
        candidates = fused_results[:candidate_limit]

        if settings.enable_reranker:
            ranked = self.reranker.rerank(
                request.query,
                candidates,
                top_k=final_k,
            )
            return ranked

        return [
            RetrievalResult(
                chunk_id=item.chunk.chunk_id,
                document_id=item.chunk.document_id,
                tenant_id=item.chunk.tenant_id,
                content=item.chunk.content,
                source=item.chunk.source,
                method="hybrid",
                rank=rank,
                score=item.fused_score,
                metadata={
                    **item.chunk.metadata,
                    "rrf_score": item.fused_score
                },
            )
            for rank, item in enumerate(
                candidates[:final_k],
                start=1,
            )
        ]








