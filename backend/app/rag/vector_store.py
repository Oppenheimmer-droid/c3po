# MODO DUMMY ACTIVADO
# Este archivo reemplaza el vector store real para permitir que el backend arranque.

def retrieval_pipeline(query: str):
    return [
        {
            "content": "MODO DUMMY: No hay RAG real. Respuesta simulada.",
            "score": 1.0
        }
    ]
