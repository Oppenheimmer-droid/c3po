"""RAG (Retrieval-Augmented Generation) pipeline components."""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
import chromadb
from chromadb.config import Settings
import chromadb.errors as chroma_errors
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class ChromaManager:
    """Manager for ChromaDB vector store operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        self._collections: Dict[str, Any] = {}
        self._initialized = True
    
    def get_collection(self, tenant_id: str) -> Any:
        """Get or create a collection for a tenant."""
        collection_name = f"tenant_{tenant_id}"
        
        if collection_name not in self._collections:
            try:
                collection = self._client.get_or_create_collection(
                    name=collection_name,
                    metadata={"tenant_id": tenant_id},
                )
                self._collections[collection_name] = collection
            except Exception as e:
                logger.error(f"Error creating collection for tenant {tenant_id}: {e}")
                # Fallback: try to get existing
                collection = self._client.get_collection(name=collection_name)
                self._collections[collection_name] = collection
        
        return self._collections[collection_name]
    
    def reset_tenant(self, tenant_id: str) -> bool:
        """Reset a tenant's collection (delete all vectors)."""
        collection_name = f"tenant_{tenant_id}"
        try:
            self._client.delete_collection(name=collection_name)
            if collection_name in self._collections:
                del self._collections[collection_name]
            return True
        except Exception as e:
            logger.error(f"Error resetting tenant collection: {e}")
            return False
    
    def reset_all(self) -> None:
        """Reset all collections."""
        self._client.reset()
        self._collections.clear()


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        self._client = None
        self._model = settings.OPENAI_EMBEDDING_MODEL
        self._dimension = settings.OPENAI_EMBEDDING_DIM
    
    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        client = self._get_client()
        response = client.embeddings.create(
            model=self._model,
            input=text,
        )
        return response.data[0].embedding
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        client = self._get_client()
        response = client.embeddings.create(
            model=self._model,
            input=texts,
        )
        return [item.embedding for item in response.data]
    
    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension."""
        return self._dimension


class VectorStore:
    """Vector store operations for RAG."""
    
    def __init__(self):
        self.chroma = ChromaManager()
        self.embeddings = EmbeddingService()
    
    async def add_chunks(
        self,
        tenant_id: str,
        chunks: List[Dict[str, Any]],
    ) -> List[str]:
        """Add document chunks to vector store."""
        collection = self.chroma.get_collection(tenant_id)
        
        # Generate embeddings
        texts = [chunk["content"] for chunk in chunks]
        embeddings = await self.embeddings.embed_batch(texts)
        
        # Prepare for ChromaDB
        ids = [chunk["id"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Add to collection
        try:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
            return ids
        except Exception as e:
            logger.error(f"Error adding chunks to vector store: {e}")
            raise
    
    async def query(
        self,
        tenant_id: str,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Query the vector store for relevant chunks."""
        collection = self.chroma.get_collection(tenant_id)
        
        # Generate query embedding
        query_embedding = await self.embeddings.embed_text(query_text)
        
        # Query ChromaDB
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"],
            )
            
            # Format results
            formatted_results = []
            for i, doc_id in enumerate(results["ids"][0]):
                formatted_results.append({
                    "id": doc_id,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "score": 1 - results["distances"][0][i],  # Convert distance to similarity
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []
    
    async def delete_chunks(self, tenant_id: str, chunk_ids: List[str]) -> bool:
        """Delete chunks from vector store."""
        collection = self.chroma.get_collection(tenant_id)
        try:
            collection.delete(ids=chunk_ids)
            return True
        except Exception as e:
            logger.error(f"Error deleting chunks: {e}")
            return False
    
    async def delete_by_document(self, tenant_id: str, document_id: str) -> int:
        """Delete all chunks for a document."""
        collection = self.chroma.get_collection(tenant_id)
        try:
            results = collection.get(
                where={"document_id": document_id},
                include=["ids"],
            )
            if results["ids"]:
                chunk_ids = results["ids"]
                collection.delete(ids=chunk_ids)
                return len(chunk_ids)
            return 0
        except Exception as e:
            logger.error(f"Error deleting document chunks: {e}")
            return 0


class RetrievalPipeline:
    """Pipeline for retrieving relevant context for RAG."""
    
    def __init__(self):
        self.vector_store = VectorStore()
    
    async def retrieve(
        self,
        tenant_id: str,
        query: str,
        document_ids: Optional[List[str]] = None,
        subject_id: Optional[str] = None,
        top_k: int = 5,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Retrieve relevant chunks for a query.
        
        Returns:
            Tuple of (chunks, citations) where citations are formatted references
        """
        # Build filter
        filter_metadata = {}
        if document_ids:
            filter_metadata["document_id"] = {"$in": document_ids}
        if subject_id:
            filter_metadata["subject_id"] = subject_id
        
        # Query vector store
        results = await self.vector_store.query(
            tenant_id=tenant_id,
            query_text=query,
            n_results=top_k,
            filter_metadata=filter_metadata if filter_metadata else None,
        )
        
        if not results:
            return [], []
        
        # Format citations
        citations = []
        for result in results:
            citation = {
                "chunk_id": result["id"],
                "source": result["metadata"].get("source", "Unknown"),
                "page": result["metadata"].get("page"),
                "text": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
            }
            citations.append(citation)
        
        return results, citations
    
    async def retrieve_for_evaluation(
        self,
        tenant_id: str,
        document_id: str,
        topic: str,
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve chunks for evaluation question generation."""
        results = await self.vector_store.query(
            tenant_id=tenant_id,
            query_text=topic,
            n_results=count,
            filter_metadata={"document_id": document_id},
        )
        return results


# Global instances
vector_store = VectorStore()
retrieval_pipeline = RetrievalPipeline()