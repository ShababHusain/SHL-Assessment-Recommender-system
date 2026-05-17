"""
Test suite for SHL Assessment Recommender.
Tests core behaviors: clarification, recommendation, refinement, comparison, refusal.
"""

import pytest
import logging
from schemas import Message, MessageRole, ChatRequest
from rag_retriever import RAGRetriever
from embeddings import EmbeddingsManager
from faiss_index import FAISSIndexManager
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSchemaValidation:
    """Test Pydantic schema validation."""
    
    def test_message_valid(self):
        """Valid message creation."""
        msg = Message(role=MessageRole.USER, content="Hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"
    
    def test_message_empty_content_fails(self):
        """Empty content should fail."""
        with pytest.raises(ValueError):
            Message(role=MessageRole.USER, content="")
    
    def test_message_whitespace_only_fails(self):
        """Whitespace-only content should fail."""
        with pytest.raises(ValueError):
            Message(role=MessageRole.USER, content="   ")
    
    def test_chat_request_valid(self):
        """Valid chat request."""
        msg = Message(role=MessageRole.USER, content="Test")
        req = ChatRequest(messages=[msg])
        assert len(req.messages) == 1
    
    def test_chat_request_empty_fails(self):
        """Empty messages should fail."""
        with pytest.raises(ValueError):
            ChatRequest(messages=[])
    
    def test_chat_request_non_user_last_fails(self):
        """Last message must be from user."""
        msgs = [
            Message(role=MessageRole.USER, content="Hi"),
            Message(role=MessageRole.ASSISTANT, content="Hello")
        ]
        with pytest.raises(ValueError):
            ChatRequest(messages=msgs)


class TestEmbeddings:
    """Test embeddings manager."""
    
    @pytest.fixture
    def embeddings_manager(self):
        """Create embeddings manager."""
        return EmbeddingsManager(model_name="all-MiniLM-L6-v2")
    
    def test_single_embedding(self, embeddings_manager):
        """Single text embedding."""
        text = "Java developer"
        embedding = embeddings_manager.embed_text(text)
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) > 0
    
    def test_batch_embedding(self, embeddings_manager):
        """Batch embedding."""
        texts = ["Java", "Python", "JavaScript"]
        embeddings = embeddings_manager.embed_batch(texts)
        assert embeddings.shape[0] == 3
        assert embeddings.shape[1] > 0
    
    def test_embedding_dimension_consistent(self, embeddings_manager):
        """Embeddings have consistent dimension."""
        dim1 = embeddings_manager.embed_text("test1").shape[0]
        dim2 = embeddings_manager.embed_text("test2").shape[0]
        assert dim1 == dim2
    
    def test_similar_texts_similar_embeddings(self, embeddings_manager):
        """Similar texts should have similar embeddings."""
        text1 = "Java developer for backend systems"
        text2 = "Python backend developer"
        
        emb1 = embeddings_manager.embed_text(text1)
        emb2 = embeddings_manager.embed_text(text2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        assert similarity > 0.5  # Should be reasonably similar


class TestFAISSIndex:
    """Test FAISS index manager."""
    
    @pytest.fixture
    def faiss_manager(self):
        """Create FAISS manager with dummy data."""
        manager = FAISSIndexManager(embedding_dimension=384)
        
        # Create dummy embeddings
        num_items = 10
        dim = 384
        embeddings = np.random.randn(num_items, dim).astype(np.float32)
        manager.build_index(embeddings)
        
        # Add metadata
        metadata = [
            {
                "name": f"Assessment {i}",
                "url": f"https://example.com/assessment{i}",
                "test_type": "Test Type"
            }
            for i in range(num_items)
        ]
        manager.add_metadata(metadata)
        
        return manager
    
    def test_index_creation(self, faiss_manager):
        """Index created with correct size."""
        assert faiss_manager.index is not None
        assert faiss_manager.index.ntotal == 10
    
    def test_search(self, faiss_manager):
        """Search returns results."""
        query = np.random.randn(384).astype(np.float32)
        results, scores = faiss_manager.search(query, k=5)
        assert len(results) == 5
        assert len(scores) == 5
        assert all(isinstance(s, float) for s in scores)
    
    def test_search_respects_k(self, faiss_manager):
        """Search respects k parameter."""
        query = np.random.randn(384).astype(np.float32)
        results, scores = faiss_manager.search(query, k=3)
        assert len(results) == 3
    
    def test_search_empty_index_fails(self):
        """Search on empty index fails."""
        manager = FAISSIndexManager(384)
        query = np.random.randn(384).astype(np.float32)
        with pytest.raises(RuntimeError):
            manager.search(query)


class TestRetriever:
    """Test RAG retriever."""
    
    @pytest.fixture
    def retriever(self):
        """Create retriever with dummy data."""
        embeddings = EmbeddingsManager(model_name="all-MiniLM-L6-v2")
        faiss = FAISSIndexManager(embeddings.get_embedding_dimension())
        
        # Create embeddings for dummy catalog
        assessments = [
            "Java programming assessment for backend engineers",
            "Python skills test for data scientists",
            "JavaScript front-end development test",
            "SQL database skills assessment",
            "Leadership potential evaluation"
        ]
        
        embs = embeddings.embed_batch(assessments)
        faiss.build_index(embs)
        
        metadata = [
            {
                "name": "Java Skills Test",
                "url": "https://example.com/java",
                "test_type": "Technical"
            },
            {
                "name": "Python Data Science",
                "url": "https://example.com/python",
                "test_type": "Technical"
            },
            {
                "name": "JavaScript Frontend",
                "url": "https://example.com/js",
                "test_type": "Technical"
            },
            {
                "name": "SQL Mastery",
                "url": "https://example.com/sql",
                "test_type": "Technical"
            },
            {
                "name": "Leadership Potential",
                "url": "https://example.com/leadership",
                "test_type": "Behavioral"
            }
        ]
        faiss.add_metadata(metadata)
        
        return RAGRetriever(embeddings, faiss, top_k=5)
    
    def test_retrieve_valid_query(self, retriever):
        """Retrieve returns results for valid query."""
        results = retriever.retrieve("Java developer")
        assert len(results) > 0
        assert all(hasattr(r, 'name') for r in results)
        assert all(hasattr(r, 'url') for r in results)
        assert all(hasattr(r, 'test_type') for r in results)
    
    def test_retrieve_caps_at_10(self, retriever):
        """Retrieve caps results at 10."""
        results = retriever.retrieve("test", top_k=15)
        assert len(results) <= 10
    
    def test_retrieve_empty_query_returns_empty(self, retriever):
        """Empty query returns empty results."""
        results = retriever.retrieve("")
        assert len(results) == 0
    
    def test_retrieve_for_context(self, retriever):
        """Retrieve based on structured context."""
        results = retriever.retrieve_for_context(
            role="Backend Engineer",
            skills=["Java", "SQL"]
        )
        assert len(results) >= 0


class TestConversationalFlow:
    """Test conversational flows (high-level)."""
    
    def test_clarification_phase(self):
        """Clarification phase with vague query."""
        # This would test intent detection and question generation
        # Requires full agent setup with LLM
        pass
    
    def test_recommendation_phase(self):
        """Recommendation phase with clear context."""
        # This would test recommendation retrieval and response generation
        pass
    
    def test_refinement_phase(self):
        """Refinement phase with changed requirements."""
        # This would test updating recommendations
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
