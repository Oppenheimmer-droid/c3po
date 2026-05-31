def retrieval_pipeline(query: str):
    return {
        "chunks": [],
        "metadata": {},
        "debug": "[DUMMY VECTOR STORE]"
    }


class DummyVectorStore:
    """Dummy vector store for offline mode."""
    
    async def add_chunks(self, tenant_id: str, chunks: list) -> list:
        """Return dummy IDs for chunks."""
        return [f"dummy_{i}" for i in range(len(chunks))]
    
    async def delete_by_document(self, tenant_id: str, document_id: str):
        """No-op delete."""
        pass
    
    async def retrieve(self, tenant_id: str, query: str, top_k: int = 4) -> list:
        """Return empty results."""
        return []


# Export the dummy vector store instance
vector_store = DummyVectorStore()
