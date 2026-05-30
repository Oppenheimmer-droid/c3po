from typing import List
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document

# Objeto global que document_service.py espera
class VectorStoreWrapper:
    def __init__(self):
        self.index = None

    def init(self, documents: List[Document]):
        self.index = VectorStoreIndex.from_documents(documents)

    def retrieve(self, query: str, top_k: int = 4):
        if self.index is None:
            return []
        engine = self.index.as_query_engine(similarity_top_k=top_k)
        return engine.retrieve(query)

# Instancia global que otros módulos importan
vector_store = VectorStoreWrapper()

# API pública compatible con tu código actual
def init_vector_store(documents: List[Document]):
    vector_store.init(documents)

def retrieval_pipeline(query: str, top_k: int = 4):
    return vector_store.retrieve(query, top_k)
