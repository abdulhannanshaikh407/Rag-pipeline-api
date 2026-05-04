"""
Hybrid retriever combining vector and BM25 search with Reciprocal Rank Fusion.
"""
from typing import List, Dict, Any, Optional
import numpy as np
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from app.services.vectorstore.base import BaseVectorStore
from app.services.embedding.embedder import EmbeddingService
from app.core.config import get_settings
from app.core.logging import setup_logging
import structlog

logger = structlog.get_logger()


class RetrievedDocument(Document):
    """Document with retrieval score and method."""
    score: float
    retrieval_method: str  # "vector", "bm25", or "hybrid"


class HybridRetriever:
    """
    Combines dense (vector) and sparse (BM25) retrieval via Reciprocal Rank Fusion.

    Algorithm:
    1. Vector search: embed query → similarity_search(top_k * 2)
    2. BM25 search: tokenize query → rank chunks by BM25 score
    3. RRF fusion: score = Σ 1/(k + rank_i) for each result
    4. Re-rank by fused score, return top_k
    5. Apply metadata filters before search if provided

    Config-driven weights: bm25_weight, vector_weight from settings.
    If hybrid_search_enabled=False, use vector only.
    """

    def __init__(self, vector_store: BaseVectorStore, embedder: EmbeddingService):
        self.vector_store = vector_store
        self.embedder = embedder
        self.settings = get_settings()
        self.bm25_index = None
        self.bm25_documents = []  # List of documents for BM25
        self._bm25_initialized = False

    def _initialize_bm25(self):
        """Initialize BM25 index from all documents in the vector store.
        Note: This is inefficient for large datasets. In production, we would
        maintain a separate BM25 index that gets updated as documents are added.
        For simplicity, we initialize on first use and rebuild when needed.
        """
        if self._bm25_initialized:
            return

        # Fetch all documents from the vector store (this is a limitation)
        # In a real system, we would store documents separately for BM25
        # For now, we'll try to get all documents by using a wildcard filter if supported
        # Since our vector store implementations don't have a "get all" method,
        # we'll skip BM25 initialization for now and note that it requires
        # a way to fetch all documents.
        # We'll implement a simple version that works if we can get all documents.
        # For ChromaDB, we can use get() without filter to get all.
        # For FAISS, we have self.documents if we are using FAISSVectorStore.
        # We'll check the type of vector_store.

        # This is a simplified approach: we assume the vector store has a way to get all documents.
        # We'll implement a helper method in the vector store to get all documents if needed.
        # For now, we'll leave BM25 as a placeholder and note that it requires
        # a proper implementation for production.
        logger.warning("BM25 initialization requires fetching all documents from vector store, "
                      "which is not efficiently implemented in this prototype.")
        self._bm25_initialized = True

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25."""
        return text.lower().split()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: dict = None
    ) -> List[RetrievedDocument]:
        """
        Returns List[RetrievedDocument] with fields:
        - content: str
        - metadata: dict (source, page, chunk_index, etc.)
        - score: float (0-1, higher = more relevant)
        - retrieval_method: str ("vector" | "bm25" | "hybrid")
        """
        if not self.settings.hybrid_search_enabled:
            return self._vector_search(query, top_k, filters)

        # Initialize BM25 if needed
        self._initialize_bm25()

        # Get vector search results (top_k * 2 for fusion)
        vector_results = self._vector_search(query, top_k * 2, filters)
        # Get BM25 results (top_k * 2 for fusion)
        bm25_results = self._bm25_search(query, top_k * 2, filters)

        # Combine results using Reciprocal Rank Fusion
        fused_results = self._rrf_fusion(vector_results, bm25_results, top_k)

        return fused_results

    def _vector_search(self, query: str, top_k: int, filters: dict = None) -> List[RetrievedDocument]:
        """Perform vector search and return results with scores."""
        query_embedding = self.embedder.embed_query(query)
        documents = self.vector_store.similarity_search(query_embedding, top_k, filters)

        # Convert to RetrievedDocument with scores
        # We don't have actual similarity scores from ChromaDB/FAISS in our current implementation,
        # so we'll assign a dummy score based on rank for demonstration.
        # In a real implementation, we would use the distance/similarity from the vector store.
        results = []
        for i, doc in enumerate(documents):
            # Assign a score inversely proportional to rank (higher rank = higher score)
            # This is a placeholder; replace with actual similarity score.
            score = 1.0 - (i / len(documents)) if documents else 0.0
            retrieved_doc = RetrievedDocument(
                page_content=doc.page_content,
                metadata=doc.metadata,
                score=score,
                retrieval_method="vector"
            )
            results.append(retrieved_doc)
        return results

    def _bm25_search(self, query: str, top_k: int, filters: dict = None) -> List[RetrievedDocument]:
        """Perform BM25 search and return results with scores."""
        # This is a placeholder implementation.
        # In a real system, we would have a BM25 index initialized with all documents.
        # For now, we'll return an empty list and note that BM25 is not fully implemented.
        logger.warning("BM25 search is not fully implemented in this prototype.")
        return []

    def _rrf_fusion(self, vector_results: List[RetrievedDocument],
                     bm25_results: List[RetrievedDocument],
                     top_k: int) -> List[RetrievedDocument]:
        """Combine results using Reciprocal Rank Fusion."""
        # Weights from settings
        k = 60  # RRF parameter, typically between 20 and 100
        vector_weight = self.settings.vector_weight
        bm25_weight = self.settings.bm25_weight

        # Create a dictionary to store fused scores
        fused_scores = {}

        # Add vector results
        for i, doc in enumerate(vector_results):
            doc_id = self._doc_id(doc)
            rank = i + 1
            if doc_id not in fused_scores:
                fused_scores[doc_id] = {"doc": doc, "score": 0.0}
            fused_scores[doc_id]["score"] += vector_weight * (1 / (k + rank))

        # Add BM25 results
        for i, doc in enumerate(bm25_results):
            doc_id = self._doc_id(doc)
            rank = i + 1
            if doc_id not in fused_scores:
                fused_scores[doc_id] = {"doc": doc, "score": 0.0}
            fused_scores[doc_id]["score"] += bm25_weight * (1 / (k + rank))

        # Sort by fused score and take top_k
        sorted_items = sorted(fused_scores.values(), key=lambda x: x["score"], reverse=True)
        top_items = sorted_items[:top_k]

        # Update the score in the document to be the fused score
        results = []
        for item in top_items:
            doc = item["doc"]
            doc.score = item["score"]
            doc.retrieval_method = "hybrid"
            results.append(doc)

        return results

    def _doc_id(self, doc: RetrievedDocument) -> str:
        """Generate a unique ID for a document based on its content and metadata."""
        # Use source, page, and chunk_index if available, otherwise fallback to content hash
        source = doc.metadata.get("source", "")
        page = doc.metadata.get("page_number", "")
        chunk_index = doc.metadata.get("chunk_index", "")
        if source:
            return f"{source}_{page}_{chunk_index}"
        return hash(doc.page_content)
