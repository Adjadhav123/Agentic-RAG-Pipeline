from attr.validators import min_len
from pydantic import BaseModel, ConfigDict, Field

class CitationResponse(BaseModel):
    model_config=ConfigDict(extra="forbid")

    citation_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    excerpt: str = Field(max_length=1000)