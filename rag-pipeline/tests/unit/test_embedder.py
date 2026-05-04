import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.services.embedding.embedder import EmbeddingService

class TestEmbeddingService:
    @patch("app.services.embedding.embedder.get_settings")
    @patch("app.services.embedding.embedder.SentenceTransformer")
    def test_embed_returns_list_of_lists(self, mock_model_class, mock_settings):
        """Test that embed_texts returns a list of lists of floats."""
        # Setup mock settings
        mock_settings.return_value.embedding_provider = "huggingface"
        mock_settings.return_value.embedding_model = "all-MiniLM-L6-v2"
        mock_settings.return_value.embedding_dimensions = 384
        mock_settings.return_value.redis_url = "redis://localhost:6379/0"
        mock_settings.return_value.cache_ttl = 3600
        mock_settings.return_value.llm_provider = "openai"
        mock_settings.return_value.openai_base_url = None

        # Mock the huggingface model to return a numpy array
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1] * 384, [0.2] * 384])
        mock_model_class.return_value = mock_model

        service = EmbeddingService()
        embeddings = service.embed_texts(["Hello world", "RAG pipeline test"])
        assert len(embeddings) == 2
        assert all(isinstance(e, list) for e in embeddings)
        assert all(isinstance(v, float) for v in embeddings[0])

    @patch("app.services.embedding.embedder.get_settings")
    @patch("app.services.embedding.embedder.SentenceTransformer")
    def test_embed_empty_list_returns_empty(self, mock_model_class, mock_settings):
        """Test that embedding an empty list returns an empty list."""
        mock_settings.return_value.embedding_provider = "huggingface"
        mock_settings.return_value.openai_base_url = None

        service = EmbeddingService()
        result = service.embed_texts([])
        assert result == []

    @patch("app.services.embedding.embedder.get_settings")
    @patch("app.services.embedding.embedder.SentenceTransformer")
    def test_embed_single_text(self, mock_model_class, mock_settings):
        """Test embedding a single text string."""
        mock_settings.return_value.embedding_provider = "huggingface"
        mock_settings.return_value.embedding_model = "all-MiniLM-L6-v2"
        mock_settings.return_value.embedding_dimensions = 384
        mock_settings.return_value.redis_url = "redis://localhost:6379/0"
        mock_settings.return_value.cache_ttl = 3600
        mock_settings.return_value.llm_provider = "openai"
        mock_settings.return_value.openai_base_url = None

        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1] * 384])
        mock_model_class.return_value = mock_model

        service = EmbeddingService()
        embeddings = service.embed_texts(["Single text"])
        assert len(embeddings) == 1
        assert len(embeddings[0]) > 0

    @patch("app.services.embedding.embedder.get_settings")
    @patch("app.services.embedding.embedder.SentenceTransformer")
    def test_embed_query(self, mock_model_class, mock_settings):
        """Test the embed_query convenience method."""
        mock_settings.return_value.embedding_provider = "huggingface"
        mock_settings.return_value.embedding_model = "all-MiniLM-L6-v2"
        mock_settings.return_value.embedding_dimensions = 384
        mock_settings.return_value.redis_url = "redis://localhost:6379/0"
        mock_settings.return_value.cache_ttl = 3600
        mock_settings.return_value.llm_provider = "openai"
        mock_settings.return_value.openai_base_url = None

        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1] * 384])
        mock_model_class.return_value = mock_model

        service = EmbeddingService()
        embedding = service.embed_query("Test query")
        assert isinstance(embedding, list)
        assert all(isinstance(v, float) for v in embedding)
