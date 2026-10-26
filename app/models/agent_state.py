from typing import TypedDict, Any 

from app.models.retrieval import RetrievalResult


class AgentState(TypedDict, total=False):
    question: str 
    tenant_id: str 
    top_k: int 

    route: str 
    search_query: str 
    documents: list[RetrievalResult]

    attempt_count: int 
    evidence_sufficient: bool 
    evidence_reason: str 

    answer: str 
    citation_ids: list[str]
    error_code: str | None 
    request_id: str 
    filters: dict[str, Any]

