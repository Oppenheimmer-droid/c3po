import uuid
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts
from app.services.chroma_client import get_collection

def index_document(text, source="tutor"):
    doc_id = str(uuid.uuid4())
    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)
    col = get_collection()

    if col is None:
        return {"indexed_chunks": 0, "doc_id": doc_id, "error": "ChromaDB not available"}

    col.add(
        ids=[f"{doc_id}_{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings,
        metadatas=[{"source": source}] * len(chunks)
    )

    return {"indexed_chunks": len(chunks), "doc_id": doc_id}
