#!/bin/bash

echo "🚀 Activando MODO DUMMY RAG (forzado)..."

# 1. Crear mock de RAGService
echo "📦 Creando mock RAGService..."
cat << 'EOF' > services/rag_service_dummy.py
class RAGService:
    def __init__(self, *args, **kwargs):
        pass

    async def run(self, *args, **kwargs):
        return {
            "answer": "RAG desactivado temporalmente (modo dummy).",
            "sources": []
        }
EOF

# 2. Forzar chat.py a usar el dummy
echo "🛠 Parcheando api/v1/chat.py..."
sed -i 's/from app.services.rag_service import RAGService/from app.services.rag_service_dummy import RAGService/' api/v1/chat.py

# 3. Sobrescribir rag_service.py para que NO importe nada real
echo "🛠 Sobrescribiendo services/rag_service.py..."
cat << 'EOF' > services/rag_service.py
# MODO DUMMY ACTIVADO
from app.services.rag_service_dummy import RAGService
EOF

# 4. Sobrescribir vector_store.py para desactivar completamente el pipeline
echo "🛠 Sobrescribiendo rag/vector_store.py..."
cat << 'EOF' > rag/vector_store.py
# MODO DUMMY ACTIVADO — vector_store deshabilitado temporalmente

def retrieval_pipeline(*args, **kwargs):
    return []
EOF

echo "✅ MODO DUMMY RAG ACTIVADO (forzado)"
echo "👉 Ahora ejecuta:"
echo "git add ."
echo "git commit -m 'Modo dummy RAG (forzado)'"
echo "git push"
