"""
Vector Store - ChromaDB-based semantic search for RAG.
Provides async operations for efficient document retrieval.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    id: str
    content: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None


@dataclass
class RetrievalResult:
    """Result from vector store retrieval."""
    chunks: List[Chunk]
    query: str
    total_retrieved: int
    collection_name: str
    latency_ms: float


class VectorStore:
    """
    Production-ready ChromaDB vector store for semantic search.
    
    Features:
    - Async/await operations
    - Automatic collection management
    - Distance metrics (cosine, L2, etc.)
    - Metadata filtering
    - Batch operations
    """
    
    DEFAULT_TOP_K = 4
    MAX_TOP_K = 20
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        persist_directory: Optional[str] = None,
    ):
        self.host = host or os.getenv("CHROMA_HOST", "localhost")
        self.port = port or int(os.getenv("CHROMA_PORT", "8000"))
        self.persist_directory = persist_directory or os.getenv(
            "CHROMA_PERSIST_DIR", "./chroma_data"
        )
        self._client = None
        self._embedding_function = None
    
    def _get_client(self):
        """Lazy initialization of ChromaDB client."""
        if self._client is not None:
            return self._client
        
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Use persistent client for local development
            if self.host in ("localhost", "127.0.0.1") and not self._is_docker():
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                    )
                )
                logger.info(f"ChromaDB persistent client at: {self.persist_directory}")
            else:
                # Use HTTP client for remote deployments
                self._client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    settings=Settings(
                        anonymized_telemetry=False,
                    )
                )
                # Verify connection
                self._client.heartbeat()
                logger.info(f"ChromaDB HTTP client at {self.host}:{self.port}")
            
            return self._client
            
        except ImportError:
            logger.error("ChromaDB not installed. Run: pip install chromadb")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            return None
    
    @staticmethod
    def _is_docker() -> bool:
        """Check if running inside a Docker container."""
        return os.path.exists("/.dockerenv")
    
    def _get_embedding_function(self):
        """Get embedding function (uses sentence-transformers)."""
        if self._embedding_function is not None:
            return self._embedding_function
        
        try:
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
            self._embedding_function = SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            logger.info("Embedding function loaded: all-MiniLM-L6-v2")
            return self._embedding_function
        except ImportError:
            logger.warning("sentence-transformers not installed. Using default embeddings.")
            return None
        except Exception as e:
            logger.warning(f"Failed to load embedding function: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if ChromaDB is available."""
        try:
            client = self._get_client()
            if client:
                client.heartbeat()
                return True
            return False
        except Exception:
            return False
    
    async def add_chunks(
        self,
        tenant_id: str,
        chunks: List[Dict[str, Any]],
        collection_name: Optional[str] = None,
    ) -> List[str]:
        """
        Add text chunks to the vector store.
        
        Args:
            tenant_id: Tenant identifier for namespace
            chunks: List of chunk dicts with 'content' and optional 'id', 'metadata'
            collection_name: Optional custom collection name
            
        Returns:
            List of chunk IDs
        """
        client = self._get_client()
        if not client:
            raise RuntimeError("ChromaDB not available")
        
        collection_name = collection_name or f"tenant_{tenant_id}"
        
        def _sync_add():
            try:
                collection = client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                
                ids = []
                documents = []
                metadatas = []
                
                for i, chunk in enumerate(chunks):
                    chunk_id = chunk.get("id", f"{tenant_id}_{i}")
                    content = chunk.get("content", "")
                    metadata = chunk.get("metadata", {})
                    metadata["tenant_id"] = tenant_id
                    
                    ids.append(str(chunk_id))
                    documents.append(content)
                    metadatas.append(metadata)
                
                if documents:
                    collection.add(
                        ids=ids,
                        documents=documents,
                        metadatas=metadatas,
                    )
                
                logger.info(f"Added {len(documents)} chunks to collection '{collection_name}'")
                return ids
                
            except Exception as e:
                logger.error(f"Error adding chunks: {e}")
                raise
        
        # Run sync operation in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_add)
    
    async def retrieve(
        self,
        tenant_id: str,
        query: str,
        top_k: int = 4,
        collection_name: Optional[str] = None,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """
        Retrieve relevant chunks for a query using semantic search.
        
        Args:
            tenant_id: Tenant identifier
            query: Search query text
            top_k: Number of results to return (max 20)
            collection_name: Optional custom collection name
            where_filter: Optional metadata filter
            
        Returns:
            List of Chunk objects ordered by relevance
        """
        client = self._get_client()
        if not client:
            raise RuntimeError("ChromaDB not available")
        
        collection_name = collection_name or f"tenant_{tenant_id}"
        top_k = min(top_k, self.MAX_TOP_K)
        
        def _sync_retrieve():
            try:
                collection = client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                
                results = collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    where=where_filter,
                )
                
                chunks = []
                if results and results.get("documents"):
                    docs = results["documents"][0]
                    ids = results.get("ids", [[]])[0]
                    metadatas = results.get("metadatas", [[]])[0]
                    distances = results.get("distances", [[]])[0]
                    
                    for i, doc in enumerate(docs):
                        chunk = Chunk(
                            id=ids[i] if i < len(ids) else f"chunk_{i}",
                            content=doc,
                            metadata=metadatas[i] if i < len(metadatas) else {},
                            distance=distances[i] if i < len(distances) else None,
                        )
                        chunks.append(chunk)
                
                logger.debug(f"Retrieved {len(chunks)} chunks for query: {query[:50]}...")
                return chunks
                
            except Exception as e:
                logger.error(f"Retrieval failed: {e}")
                raise
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_retrieve)
    
    async def delete_by_document(
        self,
        tenant_id: str,
        document_id: str,
        collection_name: Optional[str] = None,
    ) -> bool:
        """
        Delete all chunks associated with a document.
        
        Args:
            tenant_id: Tenant identifier
            document_id: Document ID to delete
            collection_name: Optional custom collection name
            
        Returns:
            True if deletion was successful
        """
        client = self._get_client()
        if not client:
            raise RuntimeError("ChromaDB not available")
        
        collection_name = collection_name or f"tenant_{tenant_id}"
        
        def _sync_delete():
            try:
                collection = client.get_or_create_collection(name=collection_name)
                collection.delete(where={"document_id": document_id})
                logger.info(f"Deleted chunks for document: {document_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting chunks: {e}")
                raise
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_delete)
    
    async def get_collection_stats(
        self,
        tenant_id: str,
        collection_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get statistics about a collection."""
        client = self._get_client()
        if not client:
            return {"count": 0, "available": False}
        
        collection_name = collection_name or f"tenant_{tenant_id}"
        
        def _sync_stats():
            try:
                collection = client.get_collection(name=collection_name)
                return {
                    "count": collection.count(),
                    "name": collection_name,
                    "available": True,
                }
            except Exception:
                return {"count": 0, "name": collection_name, "available": False}
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_stats)
    
    async def reset_collection(
        self,
        tenant_id: str,
        collection_name: Optional[str] = None,
    ) -> bool:
        """Reset (delete) a collection."""
        client = self._get_client()
        if not client:
            raise RuntimeError("ChromaDB not available")
        
        collection_name = collection_name or f"tenant_{tenant_id}"
        
        def _sync_reset():
            try:
                client.delete_collection(name=collection_name)
                logger.info(f"Reset collection: {collection_name}")
                return True
            except Exception as e:
                logger.error(f"Error resetting collection: {e}")
                raise
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_reset)


# Synchronous wrapper for backward compatibility
class VectorStoreSync:
    """Synchronous wrapper for VectorStore."""
    
    def __init__(self, **kwargs):
        self._async_store = VectorStore(**kwargs)
    
    def add_chunks(self, tenant_id: str, chunks: List[Dict]) -> List[str]:
        """Sync wrapper for add_chunks."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self._async_store.add_chunks(tenant_id, chunks)
            )
        finally:
            loop.close()
    
    def retrieve(self, tenant_id: str, query: str, top_k: int = 4) -> List[Dict]:
        """Sync wrapper for retrieve."""
        loop = asyncio.new_event_loop()
        try:
            chunks = loop.run_until_complete(
                self._async_store.retrieve(tenant_id, query, top_k)
            )
            return [
                {"id": c.id, "content": c.content, "metadata": c.metadata}
                for c in chunks
            ]
        finally:
            loop.close()


def retrieval_pipeline(
    query: str,
    tenant_id: str = None,
    top_k: int = 4,
    collection_name: str = None,
) -> Dict[str, Any]:
    """
    Synchronous retrieval pipeline for RAG queries.
    
    Args:
        query: Search query
        tenant_id: Tenant identifier
        top_k: Number of results
        collection_name: Optional collection name
        
    Returns:
        Dict with 'chunks', 'metadata', 'debug'
    """
    if not tenant_id:
        return {
            "chunks": [],
            "metadata": {"retrieval_count": 0},
            "debug": "No tenant_id provided"
        }
    
    import time
    start = time.time()
    
    try:
        vs = VectorStoreSync()
        chunks = vs.retrieve(tenant_id, query, top_k)
        elapsed_ms = int((time.time() - start) * 1000)
        
        return {
            "chunks": chunks,
            "metadata": {
                "retrieval_count": len(chunks),
                "latency_ms": elapsed_ms,
            },
            "debug": "ChromaDB" if chunks else "No results"
        }
    except Exception as e:
        return {
            "chunks": [],
            "metadata": {"retrieval_count": 0},
            "debug": f"Error: {str(e)}"
        }


# Singleton instances
vector_store = VectorStore()
vector_store_sync = VectorStoreSync()
