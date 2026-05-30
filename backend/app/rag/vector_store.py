from typing import List, Any
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document

_index = None

def init_vector_store(documents: List[Document]):
    global _index
    _index = VectorStoreIndex.from_documents(documents)

def retrieval_pipeline(query: str, top_k: int = 4):
    if _index is None:
        return []
    engine = _index.as_query_engine(similarity_top_k=top_k)
    return engine.retrieve(query)
