"""Document repository for database operations."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Document, DocumentChunk, Subject, Topic
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Document, db)
    
    async def get_by_tenant(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Document]:
        """Get documents for a tenant."""
        query = select(Document).where(Document.tenant_id == tenant_id)
        
        if status:
            query = query.where(Document.status == status)
        
        result = await self.db.execute(
            query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_by_tenant(self, tenant_id: UUID, status: Optional[str] = None) -> int:
        """Count documents for a tenant."""
        query = select(func.count()).select_from(Document).where(Document.tenant_id == tenant_id)
        if status:
            query = query.where(Document.status == status)
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_by_subject(
        self, tenant_id: UUID, subject_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """Get documents by subject."""
        result = await self.db.execute(
            select(Document)
            .where(
                and_(
                    Document.tenant_id == tenant_id,
                    Document.subject_id == subject_id,
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_status(
        self, doc_id: UUID, status: str, error_message: Optional[str] = None
    ) -> Optional[Document]:
        """Update document processing status."""
        values = {"status": status}
        if error_message:
            values["error_message"] = error_message
        
        await self.db.execute(
            select(Document).where(Document.id == doc_id).values(**values)
        )
        await self.db.flush()
        return await self.get_by_id(doc_id)
    
    async def update_chunk_count(self, doc_id: UUID, chunk_count: int) -> None:
        """Update document chunk count after processing."""
        await self.db.execute(
            select(Document).where(Document.id == doc_id).values(chunk_count=chunk_count)
        )
        await self.db.flush()


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    """Repository for DocumentChunk operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(DocumentChunk, db)
    
    async def get_by_document(
        self, document_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[DocumentChunk]:
        """Get chunks for a document."""
        result = await self.db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_by_document(self, document_id: UUID) -> int:
        """Count chunks for a document."""
        result = await self.db.execute(
            select(func.count())
            .select_from(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
        )
        return result.scalar() or 0
    
    async def delete_by_document(self, document_id: UUID) -> int:
        """Delete all chunks for a document."""
        from sqlalchemy import delete
        result = await self.db.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        await self.db.flush()
        return result.rowcount
    
    async def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[DocumentChunk]:
        """Get chunks by vector IDs."""
        result = await self.db.execute(
            select(DocumentChunk).where(DocumentChunk.vector_id.in_(chunk_ids))
        )
        return list(result.scalars().all())


class SubjectRepository(BaseRepository[Subject]):
    """Repository for Subject operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Subject, db)
    
    async def get_by_tenant(self, tenant_id: UUID) -> List[Subject]:
        """Get all subjects for a tenant."""
        result = await self.db.execute(
            select(Subject)
            .where(Subject.tenant_id == tenant_id)
            .order_by(Subject.name)
        )
        return list(result.scalars().all())
    
    async def get_by_code(self, tenant_id: UUID, code: str) -> Optional[Subject]:
        """Get subject by code within a tenant."""
        result = await self.db.execute(
            select(Subject).where(
                and_(Subject.tenant_id == tenant_id, Subject.code == code)
            )
        )
        return result.scalar_one_or_none()


class TopicRepository(BaseRepository[Topic]):
    """Repository for Topic operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Topic, db)
    
    async def get_by_subject(self, subject_id: UUID) -> List[Topic]:
        """Get all topics for a subject."""
        result = await self.db.execute(
            select(Topic)
            .where(Topic.subject_id == subject_id)
            .order_by(Topic.order_index)
        )
        return list(result.scalars().all())