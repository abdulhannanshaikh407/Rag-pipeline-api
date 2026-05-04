"""
Unified embedding service supporting OpenAI and HuggingFace with caching and retry logic.
"""
import hashlib
import time
from typing import List
import openai
from anthropic import Anthropic
import numpy as np
from sentence_transformers import SentenceTransformer
import redis
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.exceptions import EmbeddingError
import structlog

# Initialize logger
logger = structlog.get_logger()


class EmbeddingService:
    """
    Unified embedding interface supporting OpenAI and HuggingFace.

    - OpenAI: Use openai.embeddings.create() with batch support (max 2048 inputs)
    - HuggingFace: Use sentence_transformers.SentenceTransformer
    - Both must return List[List[float]]
    - Include retry logic with exponential backoff (tenacity)
    - Cache embeddings in Redis if available (key = sha256(text))
    - Log token usage for OpenAI
    """

    def __init__(self):
        self.settings = get_settings()
        self.redis_client = None
        self._init_redis()

        # Initialize HuggingFace model if needed
        if self.settings.embedding_provider == "huggingface":
            self.hf_model = SentenceTransformer(self.settings.embedding_model)

        # OpenAI client
        if self.settings.llm_provider == "openai":
            self.openai_client = openai.AsyncOpenAI(
                api_key=self.settings.openai_api_key,
                base_url=getattr(self.settings, 'openai_base_url', None)
            )

    def _init_redis(self):
        """Initialize Redis client if available."""
        try:
            self.redis_client = redis.from_url(self.settings.redis_url)
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning("Failed to connect to Redis, caching disabled", error=str(e))
            self.redis_client = None

    def _get_cache_key(self, text: str) -> str:
        """Generate a cache key for the text."""
        return f"embedding:{hashlib.sha256(text.encode()).hexdigest()}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings from OpenAI API with retry logic."""
        try:
            response = await self.openai_client.embeddings.create(
                input=texts,
                model=self.settings.embedding_model
            )
            # Log token usage
            logger.info(
                "OpenAI embedding request",
                tokens_used=response.usage.total_tokens,
                model=self.settings.embedding_model
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error("OpenAI embedding failed", error=str(e))
            raise EmbeddingError(f"OpenAI embedding failed: {str(e)}")

    def _embed_huggingface(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings from HuggingFace model."""
        try:
            embeddings = self.hf_model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error("HuggingFace embedding failed", error=str(e))
            raise EmbeddingError(f"HuggingFace embedding failed: {str(e)}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts.
        Uses caching and batching for efficiency.
        """
        if not texts:
            return []

        # Check cache first
        cached_embeddings = {}
        uncached_texts = []
        uncached_indices = []

        if self.redis_client:
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text)
                cached = self.redis_client.get(cache_key)
                if cached:
                    cached_embeddings[i] = [float(x) for x in cached.decode().split(',')]
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))

        # Get embeddings for uncached texts
        new_embeddings = []
        if uncached_texts:
            if self.settings.embedding_provider == "openai":
                # Use async method but run synchronously for simplicity in this context
                # In a real async context, you would await this
                import asyncio
                new_embeddings = asyncio.run(self._embed_openai(uncached_texts))
            else:  # huggingface
                new_embeddings = self._embed_huggingface(uncached_texts)

            # Cache new embeddings
            if self.redis_client and new_embeddings:
                for idx, embedding in zip(uncached_indices, new_embeddings):
                    cache_key = self._get_cache_key(texts[idx])
                    # Store as comma-separated string for simplicity
                    self.redis_client.setex(
                        cache_key,
                        self.settings.cache_ttl,
                        ','.join(str(x) for x in embedding)
                    )

        # Combine cached and new embeddings in original order
        result = [None] * len(texts)
        for idx, embedding in cached_embeddings.items():
            result[idx] = embedding
        for idx, embedding in zip(uncached_indices, new_embeddings):
            result[idx] = embedding

        return result

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string."""
        embeddings = self.embed_texts([query])
        return embeddings[0]

    def _batch_embed(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Embed texts in batches to avoid API limits."""
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embed_texts(batch)
            all_embeddings.extend(batch_embeddings)
        return all_embeddings