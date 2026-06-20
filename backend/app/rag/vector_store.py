import os
import logging

logger = logging.getLogger(__name__)

# ChromaDB configuration
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))


class ChromaVectorStore:
    """ChromaDB vector store implementation."""

    def __init__(self):
        self._client = None
        self._available = False
        self._init_client()

    def _init_client(self):
        """Initialize ChromaDB client if configured."""
        if not CHROMA_HOST:
            logger.warning("CHROMA_HOST not configured, using fallback mode")
            return
        
        try:
            import chromadb
            from chromadb.config import Settings
            
            # ChromaDB HttpClient - without api_version parameter
            self._client = chromadb.HttpClient(
                host=CHROMA_HOST,
                port=CHROMA_PORT,
            )
            # Test connection
            self._client.heartbeat()
            self._available = True
            logger.info(f"ChromaDB connected at {CHROMA_HOST}:{CHROMA_PORT}")
        except ImportError:
            logger.warning("ChromaDB not installed, using fallback mode")
        except Exception as e:
            logger.warning(f"ChromaDB not available: {e}. Using fallback mode.")
            self._client = None
            self._available = False

    async def add_chunks(self, tenant_id: str, chunks: list) -> list:
        """Add chunks to ChromaDB."""
        if not self._available or not self._client:
            return [f"dummy_{i}" for i in range(len(chunks))]
        
        try:
            collection = self._client.get_or_create_collection(
                name=f"tenant_{tenant_id}",
                metadata={"hnsw:space": "cosine"}
            )
            ids = [f"{tenant_id}_{chunk.get('id', i)}" for i, chunk in enumerate(chunks)]
            documents = [chunk.get("content", "") for chunk in chunks]
            metadatas = [chunk.get("metadata", {}) for chunk in chunks]
            collection.add(ids=ids, documents=documents, metadatas=metadatas)
            return ids
        except Exception as e:
            logger.error(f"Error adding chunks to ChromaDB: {e}")
            return [f"dummy_{i}" for i in range(len(chunks))]

    async def delete_by_document(self, tenant_id: str, document_id: str):
        """Delete chunks by document ID."""
        if not self._available or not self._client:
            return
        
        try:
            collection = self._client.get_or_create_collection(name=f"tenant_{tenant_id}")
            collection.delete(where={"document_id": document_id})
        except Exception as e:
            logger.error(f"Error deleting chunks: {e}")

    async def retrieve(self, tenant_id: str, query: str, top_k: int = 4) -> list:
        """Retrieve relevant chunks for a query."""
        if not self._available or not self._client:
            return []
        
        try:
            collection = self._client.get_or_create_collection(
                name=f"tenant_{tenant_id}",
                metadata={"hnsw:space": "cosine"}
            )
            results = collection.query(
                query_texts=[query],
                n_results=top_k
            )
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
            logger.warning(f"Vector retrieval failed: {e}")
            return []


class DummyVectorStore:
    """Dummy vector store for offline mode."""

    async def add_chunks(self, tenant_id: str, chunks: list) -> list:
        return [f"dummy_{i}" for i in range(len(chunks))]

    async def delete_by_document(self, tenant_id: str, document_id: str):
        pass

    async def retrieve(self, tenant_id: str, query: str, top_k: int = 4) -> list:
        return []


def retrieval_pipeline(query: str, tenant_id: str = None, top_k: int = 4):
    """Retrieve context for a query."""
    if not tenant_id:
        return {"chunks": [], "metadata": {}, "debug": "No tenant_id provided"}
    
    try:
        vs = ChromaVectorStore()
        chunks = vs.retrieve(tenant_id, query, top_k)
        return {
            "chunks": chunks,
            "metadata": {"retrieval_count": len(chunks)},
            "debug": "ChromaDB" if chunks else "Empty results"
        }
    except Exception as e:
        return {"chunks": [], "metadata": {}, "debug": f"Fallback: {e}"}


# Export appropriate vector store instance
try:
    vector_store = ChromaVectorStore()
except Exception:
    vector_store = DummyVectorStore()
    logger.warning("Using DummyVectorStore as fallback")
