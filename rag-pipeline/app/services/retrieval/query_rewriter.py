"""
Query rewriting using LLM for HyDE and Query Expansion.
"""
from typing import List, Optional
import asyncio
from app.services.generation.llm_client import LLMClient
from app.services.generation.prompt_manager import PromptManager
from app.core.config import get_settings
from app.core.logging import setup_logging
import structlog
import hashlib
import redis

logger = structlog.get_logger()


class RewrittenQuery:
    """Container for rewritten query results."""
    def __init__(self, original: str, rewritten: str, method: str):
        self.original = original
        self.rewritten = rewritten
        self.method = method  # "hyde", "expansion", or "original"


class QueryRewriter:
    """
    Uses LLM to rewrite the user's query for better retrieval.

    Two techniques (run in parallel, use best result):

    1. HyDE (Hypothetical Document Embeddings):
       Prompt: "Write a detailed paragraph that would answer: {query}"
       → Embed the hypothetical answer instead of the raw query
       → Much better semantic alignment with document chunks

    2. Query Expansion:
       Prompt: "Generate 3 alternative phrasings of this question: {query}"
       → Retrieve for each, merge results, deduplicate

    Cache rewritten queries in Redis (TTL = 1 hour).
    If LLM fails, fall back to original query (never raise).
    """

    def __init__(self):
        self.settings = get_settings()
        self.llm_client = LLMClient()
        self.prompt_manager = PromptManager()
        self.redis_client = None
        self._init_redis()

    def _init_redis(self):
        """Initialize Redis client if available."""
        try:
            self.redis_client = redis.from_url(self.settings.redis_url)
            self.redis_client.ping()
            logger.info("Redis connection established for query rewriting")
        except Exception as e:
            logger.warning("Failed to connect to Redis for query rewriting", error=str(e))
            self.redis_client = None

    def _get_cache_key(self, query: str) -> str:
        """Generate a cache key for the query."""
        return f"query_rewrite:{hashlib.sha256(query.encode()).hexdigest()}"

    async def rewrite(self, query: str) -> RewrittenQuery:
        """
        Rewrite the query using HyDE and Query Expansion in parallel,
        then choose the best result (for simplicity, we'll use HyDE if available).
        Returns the rewritten query and method used.
        """
        # Check cache
        if self.redis_client:
            cache_key = self._get_cache_key(query)
            cached = self.redis_client.get(cache_key)
            if cached:
                cached_data = cached.decode().split('::', 2)
                if len(cached_data) == 3:
                    return RewrittenQuery(original=cached_data[0], rewritten=cached_data[1], method=cached_data[2])

        # Run HyDE and Query Expansion in parallel
        hyde_task = self._hyde_rewrite(query)
        expansion_task = self._query_expansion_rewrite(query)

        # Wait for both to complete
        hyde_result, expansion_result = await asyncio.gather(hyde_task, expansion_task, return_exceptions=True)

        # Handle exceptions (fallback to original)
        if isinstance(hyde_result, Exception):
            logger.warning("HyDE rewrite failed", error=str(hyde_result))
            hyde_result = RewrittenQuery(original=query, rewritten=query, method="original")
        if isinstance(expansion_result, Exception):
            logger.warning("Query expansion failed", error=str(expansion_result))
            expansion_result = RewrittenQuery(original=query, rewritten=query, method="original")

        # Choose the best result: prefer HyDE if it's not original, otherwise expansion if not original, else original
        if hyde_result.method != "original":
            chosen = hyde_result
        elif expansion_result.method != "original":
            chosen = expansion_result
        else:
            chosen = RewrittenQuery(original=query, rewritten=query, method="original")

        # Cache the result
        if self.redis_client:
            cache_value = f"{chosen.original}::{chosen.rewritten}::{chosen.method}"
            self.redis_client.setex(
                self._get_cache_key(query),
                self.settings.cache_ttl,
                cache_value
            )

        return chosen

    async def _hyde_rewrite(self, query: str) -> RewrittenQuery:
        """Generate a hypothetical document that answers the query."""
        if not self.settings.query_rewriting_enabled:
            return RewrittenQuery(original=query, rewritten=query, method="original")

        try:
            prompt = self.prompt_manager.get_prompt("QUERY_REWRITE_PROMPT").format(query=query)
            # For HyDE, we want a detailed paragraph answering the question
            # We'll adjust the prompt accordingly
            hyde_prompt = f"Write a detailed paragraph that would answer the following question: {query}"
            rewritten = await self.llm_client.generate([{"role": "user", "content": hyde_prompt}])
            return RewrittenQuery(original=query, rewritten=rewritten.strip(), method="hyde")
        except Exception as e:
            logger.error("HyDE rewrite error", error=str(e))
            raise

    async def _query_expansion_rewrite(self, query: str) -> RewrittenQuery:
        """Generate alternative phrasings of the query."""
        if not self.settings.query_rewriting_enabled:
            return RewrittenQuery(original=query, rewritten=query, method="original")

        try:
            prompt = f"Generate 3 alternative phrasings of this question: {query}"
            rewritten = await self.llm_client.generate([{"role": "user", "content": prompt}])
            # For simplicity, we'll take the first alternative or just use the original if parsing fails
            # In a full implementation, we would parse the list and use all for retrieval.
            # Here, we just return the first line as the rewritten query.
            lines = [line.strip() for line in rewritten.split('\n') if line.strip()]
            if lines:
                # Use the first alternative phrasing
                rewritten_query = lines[0]
            else:
                rewritten_query = query
            return RewrittenQuery(original=query, rewritten=rewritten_query, method="expansion")
        except Exception as e:
            logger.error("Query expansion error", error=str(e))
            raise