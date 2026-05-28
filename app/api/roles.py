from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_pipeline import answer_with_role

router = APIRouter()

class RoleQuery(BaseModel):
    query: str
    role: str

@router.post("/ask")
def ask(req: RoleQuery):
    return answer_with_role(req.query, req.role)
