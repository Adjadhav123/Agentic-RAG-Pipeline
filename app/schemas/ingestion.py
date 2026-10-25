from typing import Literal

from pydantic import BaseModel, Field

class IngestionRequest(BaseModel):
    source: str = Field(min_length=1, max_length=2000)
    tenant_id: str = Field(min_length=1, max_length=128)
    content: str = Field(min_length=1, max_length=2_000_000)
    metadata: dict[str, str | int| float | bool] = Field(
        default_factory=dict
    )

class IngestionResponse(BaseModel):
    document_id: str 
    status: Literal["pending", "processing", "indexed", "failed"]
    chunks_indexed: int = Field(ge=0)

    