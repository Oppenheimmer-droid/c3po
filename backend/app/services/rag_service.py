class RAGService:
    def __init__(self):
        pass

    def query(self, text: str):
        return {
            "answer": f"[MOCK] Respuesta dummy para: {text}",
            "sources": []
        }
