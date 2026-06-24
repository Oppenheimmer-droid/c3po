"""
embeddings.py — Text embedding service.
Uses OpenAI embeddings when OPENAI_API_KEY is set, otherwise raises a clear error.
Called only from sync Celery workers (via asyncio.run), not from async FastAPI paths.
"""
import os
from typing import List




def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts.
    Uses OpenAI text-embedding-3-small.
    Must only be called from synchronous contexts (Celery workers).
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is required for document embedding. "
            "Set it in Railway environment variables or use the dummy RAG mode."
        )


    from openai import OpenAI  # imported lazily — not at module load time
    client = OpenAI(api_key=api_key)


    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    resp = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]
