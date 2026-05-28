from functools import lru_cache
from chromadb import HttpClient
from chromadb.config import Settings
import os

CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

@lru_cache
def get_chroma_client():
    return HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        ssl=True,
        api_version="v2",
        settings=Settings(chroma_api_impl="rest")
    )

def get_collection(name="tutor_knowledge"):
    return get_chroma_client().get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )
