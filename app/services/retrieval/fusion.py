from app.models.retrieval import RankedChunk, RetrievalResult

def reciprocal_rank_fusion(
    result_lists: list[list[RetrievalResult]],
    *,
    rrf_k: int = 60,
) -> list[RankedChunk]:
    """Combined multiple ranked lists using Reciprocal Rank Fusion."""

    if rrf_k < 1:
        raise ValueError("rrf_k at least 1")

    scores: dict[str, float] = {}
    chunks : dict[str, RetrievalResult] = {}

    for results in result_lists:
        seen_in_list: set[str] = set()

        for rank, result in enumerate(results, start=1):
            chunk_id = result.chunk_id

            if chunk_id in seen_in_list:
                continue
        

            seen_in_list.add(chunk_id)

            scores[chunk_id] = (
                scores.get(chunk_id, 0.0) + (1.0 / (rrf_k + rank))
            )

            chunks.setdefault(chunk_id, result)

    
    ordered_ids = sorted(
        scores,
        key=lambda chunk_id: scores[chunk_id],
        reverse=True, 
    )      

    return [
        RankedChunk(
            chunk=chunks[chunk_id], 
            fused_score=scores[chunk_id],
            total_score=rank
        )
        for rank, chunk_id in enumerate(ordered_ids, start=1)
    ] 

    

    
