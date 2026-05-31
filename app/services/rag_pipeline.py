from openai import OpenAI
import os

def get_openai_client():
    """Get OpenAI client, returns None if no API key available."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def retrieve_context(query, n=4):
    try:
        from app.services.chroma_client import get_collection
        col = get_collection()
        if col is None:
            return []
        from app.services.embeddings import embed_texts
        emb = embed_texts([query])[0]
        res = col.query(query_embeddings=[emb], n_results=n)
        return res["documents"][0]
    except Exception as e:
        # Return empty context if ChromaDB is not available
        return []

def answer_with_role(query, role="matematicas"):
    from app.core.roles import ROLES
    role_data = ROLES.get(role, ROLES["matematicas"])
    context = retrieve_context(query)
    ctx = "\n\n---\n\n".join(context)

    prompt = f"""{role_data['prompt']}

[CONTEXT]
{ctx}

[QUESTION]
{query}

Responde con estilo: {role_data['style']} y tono: {role_data['tone']}."""

    client = get_openai_client()
    
    if client:
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un tutor IA experto."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            answer = resp.choices[0].message.content
        except Exception as e:
            answer = f"[OpenAI API error: {str(e)}] Pregunta: {query}"
    else:
        answer = f"""[Modo offline - Sin clave OpenAI]

Pregunta: {query}

Respuesta del tutor ({role_data['name']}):

Lo siento, no tengo conexión a la API de OpenAI en este momento. 
Para activar el tutor IA con respuestas completas, por favor configure OPENAI_API_KEY.

Intenta con preguntas simples sobre el tema que te interese.
El estilo del tutor es: {role_data['style']}
Su tono es: {role_data['tone']}"""

    return {"query": query, "role": role, "answer": answer, "context_used": len(context) > 0}
