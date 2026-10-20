from pydantic import Field
from dataclasses import dataclass, field 
from datetime import datetime, timezone
from hashlib import sha256 
from typing import Any 
import json 


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def stable_hash(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()

def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )

@dataclass(frozen=True, slots=True)
class DocumentRecord:
    document_id: str 
    tenant_id: str 
    source: str 
    content_hash: str 
    content: str 
    version: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)

    @classmethod
    def create(
        cls,
        *,
        tenant_id: str,
        source: str,
        content: str,
        metadata: dict[str, Any] | None = None
    ) -> "DocumentRecord":
        """Created a document records."""

        normalized_source = source.replace("\\", "/")
        content_hash = stable_hash(content)

        document_id = stable_hash(
            f"{tenant_id}:{normalized_source}"
        )

        return cls(
            document_id=document_id,
            tenant_id=tenant_id,
            source=normalized_source,
            content_hash=content_hash,
            content=content,
            metadata=metadata or {}
        )


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    chunk_id: str 
    document_id: str 
    tenant_id: str 
    source: str 
    content: str 
    chunk_index: int 
    start_index: int 
    content_hash: str 
    metadata: dict[str, Any] = field(default_factory=dict)


    @classmethod
    def create(
        cls,
        *,
        document_id: str, 
        tenant_id: str,
        source: str,
        content: str,
        chunk_index: int,
        start_index: int,
        metadata: dict[str, Any] | None = None
    ) -> "DocumentChunk":

        content_hash = stable_hash(content)

        chunk_id = stable_hash(
            f"{document_id}:{start_index}:{content_hash}"
        )

        return cls(
            chunk_id=chunk_id,
            document_id=document_id,
            tenant_id=tenant_id,
            source=source,
            content=content,
            chunk_index=chunk_index,
            start_index=start_index,
            content_hash=content_hash,
            metadata=metadata or {}
        )

    def to_storage_metadata(self) -> dict[str, Any]:
        """Return flat, Chroma-compatible scalar metadata."""

        metadata = {
            key: value
            for key, value in self.metadata.items()
            if isinstance(value, (str, float, int, bool))
            and value is not None
        }

        metadata.update(
            {
                "document_id": self.document_id,
                "tenant_id": self.tenant_id,
                "source": self.source,
                "chunk_index": self.chunk_index,
                "start_index": self.start_index,
                "content_hash": self.content_hash
            }
        )

        return metadata
        

