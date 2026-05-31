class DummyVectorStore:
    def query(self, text: str):
        return {
            "chunks": [],
            "metadata": {},
            "debug": "[DUMMY VECTOR STORE]"
        }

vector_store = DummyVectorStore()

def retrieval_pipeline(query: str):
    return vector_store.query(query)
