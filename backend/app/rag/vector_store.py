import os
from chromadb import HttpClient
from chromadb.config import Settings

CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "443"))

client = HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    ssl=True,
    settings=Settings(chroma_api_impl="rest")
)

def get_collection(name="tutor_knowledge"):
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )

def retrieval_pipeline():
    return get_collection()
