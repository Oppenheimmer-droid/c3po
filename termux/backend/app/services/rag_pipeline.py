"""
rag_pipeline.py — Thin compatibility shim.
Delegates to RAGService which handles AI_PROVIDER selection (Groq / OpenAI).
Direct OpenAI sync client removed — was blocking the async event loop.
"""
import asyncio
from app.core.roles import ROLES




def answer_with_role(query: str, role: str = "matematicas", tenant_id: str = None, user_id: str = None) -> dict:
    """
    Synchronous wrapper around RAGService for legacy callers.
    Uses asyncio.run() — safe only when called from a sync context (e.g. Celery worker).
    For async FastAPI endpoints use RAGService directly.
    """
    role_data = ROLES.get(role, ROLES["matematicas"])


    async def _run():
        from app.services.rag_service import RAGService
        service = RAGService()
        result = await service.query(
            tenant_id=tenant_id,
            user_id=user_id,
            query=query,
            include_history=False,
            system_prompt_override=role_data.get("prompt"),
        )
        return result


    result = asyncio.run(_run())
    return {"query": query, "role": role, "answer": result.get("answer", "")}
