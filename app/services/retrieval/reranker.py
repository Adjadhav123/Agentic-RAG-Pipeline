from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.models.retrieval import RankedChunk, RetrievalResult
from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_reranker() -> CrossEncoder:
    settings = get_settings()

    return CrossEncoder(
        settings.reranker_model,
        max_length=512,
        device="cpu"
    )

class CrossEncoderReranker:
    def __init__(self, model: CrossEncoder | None = None) -> None:
        self._model = model

    def rerank(
        self,
        query: str, 
        candidates: list[RankedChunk],
        *,
        top_k: int,
    ) -> list[RetrievalResult]:
        """Re-rank candidates using cross-encoder model."""

        if not query.strip():
            raise ValueError("Query cannot be empty.")
        if top_k < 1: 
            raise ValueError("top_k must be at least 1")

        if not candidates:
            return []

        model = self._model or get_reranker()

        pairs = [
            (query, candidate.chunk.content)
            for candidate in candidates
        ]

        scores = model.predict(
            pairs,
            show_progress_bar=False,
        )

        ranked = sorted(
            zip(candidates, scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        results : list[RetrievalResult] = []

        for rank, (candidate, score) in enumerate(ranked[:top_k], start=1):
            original = candidate.chunk

            results.append(
                RetrievalResult(
                    chunk_id=original.chunk_id,
                    document_id=original.document_id,
                    tenant_id=original.tenant_id,
                    content=original.content,
                    source=original.source,
                    method="hybrid",
                    rank=rank,
                    score=float(score),
                    metadata={
                        **original.metadata,
                        "rrf_score": candidate.fused_score,
                        "reranker_score": float(score),
                    }
                )
            )

        return results

