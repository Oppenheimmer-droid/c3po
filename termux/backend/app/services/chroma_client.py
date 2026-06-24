import os
from functools import lru_cache
from chromadb import HttpClient
from chromadb.config import Settings


CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
CHROMA_USE_SSL = os.getenv("CHROMA_USE_CLOUD", "false").lower() == "true"




@lru_cache(maxsize=1)
def get_chroma_client() -> HttpClient:
    """
    Returns a cached ChromaDB HttpClient.
    ssl is enabled only when CHROMA_USE_CLOUD=true.
    Cache is invalidated on process restart.
    """
    return HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        ssl=CHROMA_USE_SSL,
        settings=Settings(chroma_api_impl="rest"),
    )




def get_collection(name: str = "tutor_knowledge"):
    return get_chroma_client().get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )
