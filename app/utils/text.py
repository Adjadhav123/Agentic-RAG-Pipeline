import re 
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.models.document import DocumentChunk, DocumentRecord


def normalize_text(text: str) -> str:
    """Normalize the text by removing unwanted controlled characters."""

    if not isinstance(text, str):
        raise TypeError("Document content must be a string")

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = "".join(
        char 
        for char in text 
        if char in "\n\t" or ord(char)>=32
    )

    #Removing the trailing whitespaces from each line  
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_document(document: DocumentRecord) -> list[DocumentChunk]:
    """Split a document into deterministic, searchable chunks"""

    settings = get_settings()

    content = normalize_text()

    if not content:
        raise ValueError("Document is empty after text normalization")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True
    )

    split_docs = splitter.create_documents(
        texts=[content],
        metadatas=[document.metadata],
    )

    chunks: list[DocumentChunk] = []

    for index, split_doc in enumerate(split_docs):
        chunk_content = split_doc.page_content.strip()

        if not chunk_content:
            continue

        start_index = split_doc.metadata.get("start_index", 0)

        chunk = DocumentChunk.create(
            document_id=document.document_id,
            tenant_id=document.tenant_id,
            source=document.source,
            content=chunk_content,
            chunk_index=index,
            start_index=start_index,
            metadata=document.metadata
        )

        chunks.append(chunk)

    if not chunks:
        raise ValueError("No chunk were generated from the documents.")

    return chunks