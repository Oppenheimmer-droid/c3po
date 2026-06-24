"""
Vector Store - Simple fallback sin ChromaDB para Termux/Android.
Usa búsqueda por palabras clave como alternativa cuando ChromaDB no está disponible.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Representa un chunk de texto con metadatos."""
    id: str
    content: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None


@dataclass
class RetrievalResult:
    """Resultado de la búsqueda en el vector store."""
    chunks: List[Chunk]
    query: str
    total_retrieved: int
    collection_name: str
    latency_ms: float


class VectorStoreSimple:
    """
    Vector store simple para Termux que no requiere ChromaDB.
    Usa búsqueda por palabras clave (keyword matching).
    """

    DEFAULT_TOP_K = 4
    MAX_TOP_K = 20

    def __init__(self, *args, **kwargs):
        self._collections: Dict[str, List[Dict[str, Any]]] = {}
        self.host = kwargs.get("host", "localhost")
        self.port = kwargs.get("port", 8000)
        logger.info("VectorStoreSimple inicializado (modo Termux sin ChromaDB)")

    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para búsqueda."""
        return text.lower().strip()

    def _get_keywords(self, text: str) -> set:
        """Extrae palabras clave del texto."""
        words = re.findall(r'\w+', text.lower())
        # Filtrar stop words básicas
        stop_words = {'el', 'la', 'los', 'las', 'de', 'en', 'y', 'a', 'un', 'una', 'es', 'son', 'que', 'para', 'con', 'por', 'del', 'al', 'lo', 'se', 'su', 'les', 'como', 'más', 'pero', 'o', 'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esto', 'esa', 'mi', 'tu', 'su', 'nuestro'}
        return set(w for w in words if w not in stop_words and len(w) > 2)

    def _calculate_score(self, query_keywords: set, content_keywords: set) -> float:
        """Calcula score de relevancia basado en palabras clave."""
        if not query_keywords or not content_keywords:
            return 0.0
        intersection = query_keywords & content_keywords
        union = query_keywords | content_keywords
        # Coeficiente Jaccard
        return len(intersection) / len(union) if union else 0.0

    async def create_collection(self, name: str, metadata: Optional[Dict] = None) -> bool:
        """Crea una colección."""
        if name not in self._collections:
            self._collections[name] = []
            logger.info(f"Colección '{name}' creada")
        return True

    async def add_chunks(
        self,
        collection_name: str,
        chunks: List[str],
        ids: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> bool:
        """Añade chunks a una colección."""
        if collection_name not in self._collections:
            await self.create_collection(collection_name)

        for chunk_text, chunk_id, metadata in zip(chunks, ids, metadatas):
            keywords = self._get_keywords(chunk_text)
            self._collections[collection_name].append({
                "id": chunk_id,
                "content": chunk_text,
                "metadata": metadata,
                "keywords": keywords,
            })

        logger.info(f"Añadidos {len(chunks)} chunks a '{collection_name}'")
        return True

    async def retrieve(
        self,
        collection_name: str,
        query: str,
        top_k: int = None,
        filter_metadata: Optional[Dict] = None,
    ) -> RetrievalResult:
        """Busca chunks relevantes usando búsqueda por palabras clave."""
        import time
        start = time.time()

        top_k = min(top_k or self.DEFAULT_TOP_K, self.MAX_TOP_K)

        if collection_name not in self._collections:
            logger.warning(f"Colección '{collection_name}' no encontrada")
            return RetrievalResult(
                chunks=[],
                query=query,
                total_retrieved=0,
                collection_name=collection_name,
                latency_ms=0,
            )

        query_keywords = self._get_keywords(query)

        # Calcular scores para todos los chunks
        scored_chunks = []
        for item in self._collections[collection_name]:
            # Filtrar por metadata si se especifica
            if filter_metadata:
                skip = False
                for k, v in filter_metadata.items():
                    if item["metadata"].get(k) != v:
                        skip = True
                        break
                if skip:
                    continue

            score = self._calculate_score(query_keywords, item["keywords"])
            if score > 0:
                scored_chunks.append((score, item))

        # Ordenar por score descendente
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        # Tomar top_k
        results = scored_chunks[:top_k]

        chunks = [
            Chunk(
                id=item["id"],
                content=item["content"],
                metadata=item["metadata"],
                distance=1 - score,  # Convertir score a "distancia"
            )
            for score, item in results
        ]

        latency = (time.time() - start) * 1000

        return RetrievalResult(
            chunks=chunks,
            query=query,
            total_retrieved=len(chunks),
            collection_name=collection_name,
            latency_ms=latency,
        )

    async def delete_collection(self, name: str) -> bool:
        """Elimina una colección."""
        if name in self._collections:
            del self._collections[name]
            logger.info(f"Colección '{name}' eliminada")
        return True

    async def reset(self) -> bool:
        """Resetea todas las colecciones."""
        self._collections.clear()
        logger.info("Vector store reseteado")
        return True


# Instancia global para uso como fallback
_vector_store: Optional[VectorStoreSimple] = None


def get_vector_store(*args, **kwargs) -> VectorStoreSimple:
    """Obtiene la instancia global del vector store simple."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreSimple(*args, **kwargs)
    return _vector_store
