from openai import OpenAI
import os

def get_openai_client():
    """Get OpenAI client, returns None if no API key available."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def embed_texts(texts):
    client = get_openai_client()
    if client is None:
        # Return dummy embeddings for offline mode
        return [[0.0] * 1536 for _ in texts]
    
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [d.embedding for d in resp.data]
