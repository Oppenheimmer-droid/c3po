"""Vector store implementation - ChromaDB with fallback to dummy mode."""

import os
import logging

logger = logging.getLogger(__name__)

# ChromaDB configuration
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

_chroma_client = None


def _get_chroma_client():
    """Lazy initialization of ChromaDB client."""
    global _chroma_client
    if _chroma_client is not None:
        return _chroma_client
    
    if not CHROMA_HOST:
        logger.info("CHROMA_HOST not set - using dummy mode")
        return None
    
    try:
        import chromadb
        _chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        _chroma_client.heartbeat()
        logger.info(f"ChromaDB connected at {CHROMA_HOST}:{CHROMA_PORT}")
        return _chroma_client
    except Exception as e:
        logger.warning(f"ChromaDB unavailable: {e}")
        return None


class VectorStore:
    """Vector store with ChromaDB backend and dummy fallback."""
    
    async def add_chunks(self, tenant_id: str, chunks: list) -> list:
        """Add chunks to vector store."""
        client = _get_chroma_client()
        if not client:
            return [f"dummy_{i}" for i in range(len(chunks))]
        
        try:
            collection = client.get_or_create_collection(
                name=f"tenant_{tenant_id}",
                metadata={"hnsw:space": "cosine"}
            )
            ids = [f"{tenant_id}_{chunk.get('id', i)}" for i, chunk in enumerate(chunks)]
            documents = [chunk.get("content", "") for chunk in chunks]
            collection.add(ids=ids, documents=documents)
            return ids
        except Exception as e:
            logger.error(f"Error adding chunks: {e}")
            return [f"dummy_{i}" for i in range(len(chunks))]
    
    async def delete_by_document(self, tenant_id: str, document_id: str):
        """Delete chunks by document."""
        client = _get_chroma_client()
        if not client:
            return
        try:
            collection = client.get_or_create_collection(name=f"tenant_{tenant_id}")
            collection.delete(where={"document_id": document_id})
        except Exception as e:
            logger.error(f"Error deleting chunks: {e}")
    
    async def retrieve(self, tenant_id: str, query: str, top_k: int = 4) -> list:
        """Retrieve relevant chunks."""
        client = _get_chroma_client()
        if not client:
            return []
        
        try:
            collection = client.get_or_create_collection(
                name=f"tenant_{tenant_id}",
                metadata={"hnsw:space": "cosine"}
            )
            results = collection.query(query_texts=[query], n_results=top_k)
            chunks = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    chunks.append({
                        "content": doc,
                        "id": results["ids"][0][i] if results.get("ids") else f"chunk_{i}",
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {}
                    })
            return chunks
        except Exception as e:
            logger.warning(f"Retrieval failed: {e}")
            return []


def retrieval_pipeline(query: str, tenant_id: str = None, top_k: int = 4):
    """Retrieve context for a query."""
    if not tenant_id:
        return {"chunks": [], "metadata": {}, "debug": "No tenant_id"}
    
    try:
        vs = VectorStore()
        chunks = vs.retrieve(tenant_id, query, top_k)
        return {
            "chunks": chunks,
            "metadata": {"retrieval_count": len(chunks)},
            "debug": "ChromaDB" if chunks else "Empty"
        }
    except Exception as e:
        return {"chunks": [], "metadata": {}, "debug": str(e)}


# Singleton instance
vector_store = VectorStore()
