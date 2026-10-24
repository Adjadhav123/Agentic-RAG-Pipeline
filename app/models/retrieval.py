from dis import disco
from asyncio import streams
from asyncio import streams
from typing import Any, Literal
from dataclasses import dataclass, field


RetrievalMethod = Literal[
    "bm25",
    "vector",
    "hybird",
    "sql"
]

@dataclass(frozen=True, slots=True)
class RetrievalResult:
    chunk_id: str 
    document_id: str 
    tenant_id: str 
    source: str 
    content: str 
    method: RetrievalMethod
    rank: int 
    score: float | None = None 
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_context_dict(self) -> dict[str, Any]:
        """Return a flatten dict for llm context."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "source": self.source,
            "content": self.content,
            "method": self.method,
            "rank": self.rank,
            "score": self.score,
            "metatadata": self.metadata
        }


@dataclass(frozen=True, slots=True)
class SearchRequest:
    chunk_id: str
    tenant_id: str 
    top_k: int = 10 
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RankedChunk:
    chunk: RetrievalResult 
    fused_score: str 
    total_score: int 

    