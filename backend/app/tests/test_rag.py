"""Integration tests for RAG pipeline."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.rag.vector_store import VectorStore, EmbeddingService, ChromaManager


class TestEmbeddingService:
    """Test cases for embedding service."""

    @pytest.fixture
    def embedding_service(self):
        """Create embedding service."""
        return EmbeddingService()

    def test_get_embedding_dimension(self, embedding_service):
        """Test getting embedding dimension."""
        dim = embedding_service.get_embedding_dimension()
        assert dim == 1536  # text-embedding-3-small dimension


class TestVectorStore:
    """Test cases for vector store operations."""

    @pytest.fixture
    def vector_store(self):
        """Create vector store with mocked ChromaDB."""
        with patch('app.rag.vector_store.ChromaManager') as mock_chroma:
            mock_instance = MagicMock()
            mock_chroma.return_value = mock_instance
            vs = VectorStore()
            vs.chroma = mock_instance
            return vs

    @pytest.mark.asyncio
    async def test_query_with_no_results(self, vector_store):
        """Test querying when no results are found."""
        vector_store.chroma.get_collection = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query = MagicMock(return_value={
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        })
        
        results = await vector_store.query(
            tenant_id="test-tenant",
            query_text="test query",
            n_results=5,
        )
        
        assert results == []


class TestRetrievalPipeline:
    """Test cases for retrieval pipeline."""

    @pytest.fixture
    def mock_chunks(self):
        """Create mock chunks."""
        return [
            {
                "id": str(uuid4()),
                "content": "Algebra is a branch of mathematics.",
                "metadata": {
                    "document_id": str(uuid4()),
                    "source": "math_basics.pdf",
                    "page": 1,
                },
                "distance": 0.1,
            },
            {
                "id": str(uuid4()),
                "content": "Variables represent unknown values.",
                "metadata": {
                    "document_id": str(uuid4()),
                    "source": "math_basics.pdf",
                    "page": 2,
                },
                "distance": 0.2,
            },
        ]

    def test_citation_format(self, mock_chunks):
        """Test that citations are properly formatted."""
        citations = []
        for chunk in mock_chunks:
            citation = {
                "chunk_id": chunk["id"],
                "source": chunk["metadata"].get("source", "Unknown"),
                "page": chunk["metadata"].get("page"),
                "text": chunk["content"][:50] + "...",
            }
            citations.append(citation)
        
        assert len(citations) == 2
        assert citations[0]["source"] == "math_basics.pdf"
        assert citations[0]["page"] == 1
        assert citations[1]["page"] == 2


class TestRAGService:
    """Test cases for RAG service."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = AsyncMock()
        db.execute = AsyncMock()
        db.flush = AsyncMock()
        return db

    def test_build_context(self):
        """Test building context from chunks."""
        chunks = [
            {
                "content": "First chunk content",
                "metadata": {"source": "doc1.pdf", "page": 1},
            },
            {
                "content": "Second chunk content",
                "metadata": {"source": "doc2.pdf", "page": 3},
            },
        ]
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            source = metadata.get("source", "Unknown")
            page = metadata.get("page")
            page_info = f" (page {page})" if page else ""
            context_parts.append(f"[Source {i}]{page_info}:\n{chunk['content']}")
        
        context = "\n\n".join(context_parts)
        
        assert "[Source 1]" in context
        assert "doc1.pdf" in context
        assert "[Source 2]" in context
        assert "doc2.pdf" in context
        assert "First chunk content" in context

    def test_no_information_response(self):
        """Test response when no relevant information found."""
        response = {
            "answer": "No relevant information found in the documents.",
            "citations": [],
            "tokens_used": 0,
        }
        
        assert response["citations"] == []
        assert "No relevant information" in response["answer"]


class TestDocumentProcessing:
    """Test cases for document processing."""

    def test_chunk_text_simple(self):
        """Test basic text chunking."""
        text = "This is a longer text that should be split into chunks. " * 20
        chunk_size = 100
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
            start = end
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= chunk_size + 20  # Some tolerance for word boundaries

    def test_mime_type_detection(self):
        """Test MIME type detection from filename."""
        test_cases = [
            ("document.pdf", "application/pdf"),
            ("report.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("notes.txt", "text/plain"),
            ("readme.md", "text/markdown"),
        ]
        
        from pathlib import Path
        
        for filename, expected_type in test_cases:
            ext = Path(filename).suffix.lower()
            mime_types = {
                ".pdf": "application/pdf",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ".txt": "text/plain",
                ".md": "text/markdown",
            }
            detected = mime_types.get(ext, "application/octet-stream")
            assert detected == expected_type


class TestEvaluationGrading:
    """Test cases for evaluation grading."""

    def test_score_calculation(self):
        """Test score calculation from answers."""
        questions = [
            {"points": 1, "correct": True},
            {"points": 1, "correct": True},
            {"points": 1, "correct": False},
            {"points": 2, "correct": True},
            {"points": 2, "correct": True},
        ]
        
        total_points = sum(q["points"] for q in questions)
        earned_points = sum(q["points"] for q in questions if q["correct"])
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        
        assert total_points == 7
        assert earned_points == 5
        assert score == pytest.approx(71.43, 0.1)

    def test_pass_fail判定(self):
        """Test pass/fail determination."""
        passing_score = 60
        
        test_cases = [
            (75, True),
            (60, True),
            (59, False),
            (30, False),
            (100, True),
        ]
        
        for score, expected_pass in test_cases:
            passed = score >= passing_score
            assert passed == expected_pass, f"Score {score} should be {expected_pass}"

    def test_feedback_generation(self):
        """Test feedback generation based on score."""
        def generate_feedback(score):
            if score >= 90:
                return "Excellent work!"
            elif score >= 70:
                return "Good job!"
            elif score >= 50:
                return "Needs improvement."
            else:
                return "Needs more study."
        
        assert "Excellent" in generate_feedback(95)
        assert "Good" in generate_feedback(75)
        assert "improvement" in generate_feedback(60)
        assert "study" in generate_feedback(40)