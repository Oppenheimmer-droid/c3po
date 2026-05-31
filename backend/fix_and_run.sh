#!/bin/bash
set -e

echo "🔥 Activando modo dummy..."
export DUMMY_MODE=true
export MOCK_MODE=true

echo "📦 Instalando email-validator..."
pip install email-validator --quiet || true

echo "🧪 Creando vector_store dummy..."
cat > app/rag/vector_store.py << 'EOF'
def retrieval_pipeline(query: str):
    return {
        "chunks": [],
        "metadata": {},
        "debug": "[DUMMY VECTOR STORE]"
    }
EOF

echo "🧪 Creando rag_service dummy..."
cat > app/services/rag_service.py << 'EOF'
class RAGService:
    def __init__(self):
        pass

    async def chat(self, message: str, user_id: str = None):
        return {
            "answer": f"[DUMMY RESPONSE] Recibido: {message}",
            "sources": []
        }
EOF

echo "🚀 Levantando backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

