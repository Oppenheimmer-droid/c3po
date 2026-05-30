from sqlalchemy.orm import Session
from app.models.documents import Document

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, document_id: str):
        return self.db.query(Document).filter(Document.id == document_id).first()

    def list_by_tenant(self, tenant_id: str):
        return self.db.query(Document).filter(Document.tenant_id == tenant_id).all()

    def create(self, document: Document):
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
