import os
from chromadb import HttpClient
from chromadb.config import Settings

# Variables de entorno definidas en Railway
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "443"))

# Cliente remoto ChromaDB (Railway)
client = HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    ssl=True,
    api_version="v2",
    settings=Settings(chroma_api_impl="rest")
)

def get_collection(name="tutor_knowledge"):
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )
