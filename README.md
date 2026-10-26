# Production-Ready Agentic RAG

A practical Retrieval-Augmented Generation (RAG) project built with Python, LangChain, LangGraph, FastAPI, SQLAlchemy, and Chroma.

The goal is to build a maintainable RAG system for Quality Management System (QMS) documents, including inspection procedures, defect descriptions, part numbers, and corrective actions.

> **Current progress:** Foundation, domain models, repositories, database layer, and basic document ingestion. Hybrid retrieval and the agent workflow are the next development stages.

## Features

- Configurable application settings using environment variables.
- Structured document and chunk models.
- Stable document IDs and content hashes.
- SQL-based document metadata storage.
- Chroma vector storage with local embeddings.
- Configurable text chunking with overlap.
- Document ingestion status tracking.
- Initial support for Markdown and text documents.
- Modular repositories and services.
- Unit and integration test structure.

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| API framework | FastAPI |
| Agent orchestration | LangGraph |
| LLM integration | LangChain and Groq |
| Embeddings | Hugging Face Sentence Transformers |
| Vector database | Chroma |
| Metadata database | SQLAlchemy with SQLite or PostgreSQL |
| Keyword retrieval | BM25 |
| Reranking | Cross-encoder |
| Testing | pytest |

## Project Structure

```text
agentic-rag/
├── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── models/
│   │   ├── document.py
│   │   ├── retrieval.py
│   │   └── agent_state.py
│   ├── repositories/
│   │   ├── document_repository.py
│   │   ├── vector_repository.py
│   │   ├── metadata_repository.py
│   │   ├── sql_document_repository.py
│   │   └── sql_metadata_repository.py
│   ├── infrastructure/
│   │   ├── database.py
│   │   └── vector_store.py
│   ├── services/
│   │   ├── ingestion_service.py
│   │   └── retrieval/
│   ├── schemas/
│   └── utils/
│       └── text.py
├── data/
│   └── documents/
│       └── sample_qms.md
├── scripts/
│   └── ingest_documents.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── evaluation/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Some directories will remain empty until their corresponding development steps are implemented.

## Prerequisites

- Python 3.11 or a compatible version supported by your installed dependencies.
- Git.
- An internet connection for downloading Python packages and the embedding model on first use.
- A Groq API key for the later LLM generation and agent stages. It is not required for text ingestion alone.

## 1. Clone or Open the Project

Open the project directory in VS Code and open a terminal at its root.

```powershell
cd path\to\agentic-rag
```

## 2. Create a Virtual Environment

Using `uv`:

```powershell
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

Alternatively, using standard Python:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, you can run the virtual environment's Python executable directly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Configure Environment Variables

Copy `.env.example` to `.env`.

```powershell
Copy-Item .env.example .env
```

Example configuration:

```dotenv
APP_NAME=Agentic RAG API
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
API_V1_PREFIX=/api/v1

GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
ENABLE_RERANKER=true

DOCUMENTS_DIR=data/documents
CHROMA_DIR=storage/chroma
CHROMA_COLLECTION=quality_documents

CHUNK_SIZE=900
CHUNK_OVERLAP=150
RETRIEVAL_TOP_K=10
FINAL_TOP_K=5
MAX_AGENT_ATTEMPTS=2

DATABASE_URL=sqlite:///./agentic_rag.db
API_KEY=
```

The configuration field names must match the settings defined in `app/core/config.py`. If a field is not defined there, add it before relying on that environment variable.

Never commit `.env` or API keys to Git.

## 4. Understand the Data Layer

The application separates domain models from storage implementations.

### DocumentRecord

Represents a complete source document. It stores:

- Document ID
- Tenant ID
- Source path or name
- Content hash
- Original text
- Version
- Metadata
- Creation timestamp

### DocumentChunk

Represents one searchable portion of a document. It stores:

- Chunk ID
- Parent document ID
- Tenant ID
- Chunk text
- Chunk position
- Character start index
- Content hash
- Metadata

### SQL database

Stores document content, versions, metadata, and ingestion status.

### Chroma

Stores searchable chunks, vector embeddings, and scalar metadata used for filtering.

The SQL database and Chroma have separate storage operations, so production ingestion must account for partial failures and retries.

## 5. Ingest Documents

Place `.md` or `.txt` files inside:

```text
data/documents/
```

The included sample document is:

```text
data/documents/sample_qms.md
```

Run the ingestion script:

```powershell
python -m scripts.ingest_documents
```

The first run may download the embedding model. It can take longer than subsequent runs.

Expected output will resemble:

```text
[INDEXED] sample_qms.md | chunks=1 | unchanged=False

Ingestion summary
Total: 1
Succeeded: 1
Failed: 0
```

The actual chunk count depends on the input text.

Running the script again with unchanged content should skip unnecessary indexing and report `unchanged=True`.

## 6. How Ingestion Works

1. Read a Markdown or text file.
2. Normalize the text.
3. Generate a stable document ID and content hash.
4. Split the text into overlapping chunks.
5. Generate embeddings for the chunks.
6. Index the chunks in Chroma.
7. Save the document record in SQL.
8. Mark the ingestion status as `indexed`.

If an operation fails, the service attempts to record a `failed` status.

## 7. Testing

Run the unit tests:

```powershell
python -m pytest tests/unit -v
```

Run the integration tests:

```powershell
python -m pytest tests/integration -v
```

Before running integration tests, configure `DATABASE_URL` to point to a test database. Do not run destructive integration tests against production data.

## 8. Current Limitations

This is an evolving project, not yet a complete production deployment.

- The ingestion script currently supports Markdown and text files only.
- PDF extraction and OCR have not yet been implemented.
- Hybrid retrieval, query rewriting, evidence evaluation, and answer generation are still being developed.
- The initial BM25 implementation is intended for small datasets; scalable indexing will require caching or a dedicated indexing strategy.
- SQL and Chroma do not have a shared transaction.
- Changed documents require careful replacement of obsolete vector chunks.
- The example tenant ID is for development only. Production tenant identity must come from authenticated authorization context, not a user-supplied request field.
- Database migrations, authentication, rate limiting, monitoring, and production deployment hardening must be completed before deployment.

## Development Roadmap

| Step | Work |
|---|---|
| 1 | Project foundation and configuration |
| 2 | Domain models, repositories, and database |
| 3 | Document ingestion and chunking |
| 4 | Hybrid retrieval, RRF, and reranking |
| 5 | LangGraph agent workflow |
| 6 | Answer generation and citations |
| 7 | FastAPI endpoints and security |
| 8 | Evaluation, testing, and deployment |

## License

Add your chosen license before publishing this project publicly.
