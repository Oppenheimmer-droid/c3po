from openai import OpenAI
from app.services.embeddings import embed_texts
from app.services.chroma_client import get_collection
from app.core.roles import ROLES
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def retrieve_context(query, n=4):
    col = get_collection()
    emb = embed_texts([query])[0]
    res = col.query(query_embeddings=[emb], n_results=n)
    return res["documents"][0]

def answer_with_role(query, role="matematicas"):
    role_data = ROLES.get(role, ROLES["matematicas"])
    context = retrieve_context(query)
    ctx = "\n\n---\n\n".join(context)

    prompt = f"""{role_data['prompt']}

[CONTEXT]
{ctx}

[QUESTION]
{query}

Responde con estilo: {role_data['style']} y tono: {role_data['tone']}."""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un tutor IA experto."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return {"query": query, "role": role, "answer": resp.choices[0].message.content}
