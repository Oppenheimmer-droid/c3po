# MODO DUMMY ACTIVADO
# Servicio RAG simulado para permitir que el backend arranque.

class RAGService:
    def __init__(self):
        pass

    def query(self, text: str):
        return {
            "answer": "MODO DUMMY: backend operativo sin RAG real.",
            "sources": []
        }
