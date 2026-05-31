import os
if os.getenv("DUMMY_MODE") == "true":
    retrieval_pipeline = None
    raise SystemExit("Dummy mode: RAG deshabilitado")

def retrieval_pipeline(query: str):
    return [{"content": "DUMMY RESPONSE", "score": 1.0}]
