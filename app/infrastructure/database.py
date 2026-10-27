from collections.abc import Generator

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    func
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
   sessionmaker
)

from app.core.config import get_settings

settings = get_settings()

class Base(DeclarativeBase):
    pass

class DocumentMetadataORM(Base):
    __tablename__ = "document_metadata"

    document_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    tenant_id: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
        index=True
    )

    source: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    content_hash : Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )

    metadata_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="{}"
    )

    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )


class IngestionStatusORM(Base):
    __tablename__ = "ingestion_status"

    tenant_id: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
    )

    document_id: Mapped[str] = mapped_column(
        String(128),
        primary_key=True
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False
    )

    error_message: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


is_sqlite = settings.database_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine_kwargs: dict = {
    "pool_pre_ping": True,
    "connect_args": connect_args,
}
if not is_sqlite:
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_engine(
    settings.database_url,
    **engine_kwargs
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

def init_database() -> None:
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Generator:
    with SessionLocal() as session:
        yield session