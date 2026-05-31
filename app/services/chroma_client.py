from functools import lru_cache
import os

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

@lru_cache
def get_chroma_client():
    try:
        from chromadb import HttpClient
        from chromadb.config import Settings
        return HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
            ssl=False,
            api_version="v2",
            settings=Settings(chroma_api_impl="rest")
        )
    except Exception:
        return None

def get_collection(name="tutor_knowledge"):
    client = get_chroma_client()
    if client is None:
        return None
    try:
        return client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )
    except Exception:
        return None
