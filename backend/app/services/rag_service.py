# MODO DUMMY – NO USA VECTOR STORE NI CLIENTES EXTERNOS
class RAGService:
    def __init__(self):
        pass

    async def chat(self, message: str, user_id: str = None):
        return {
            "answer": f"[DUMMY RESPONSE] Recibido: {message}",
            "sources": []
        }
