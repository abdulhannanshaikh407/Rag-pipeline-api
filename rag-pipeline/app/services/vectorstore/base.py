from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain_core.documents import Document


class BaseVectorStore(ABC):
    """Abstract interface all vector stores must implement."""

    @abstractmethod
    def add_documents(self, documents: List[Document], embeddings: List[List[float]]) -> List[str]:
        """Add documents. Returns list of generated IDs."""
        ...

    @abstractmethod
    def similarity_search(self, query_embedding: List[float], top_k: int, filters: dict = None) -> List[Document]:
        """Return top_k most similar documents."""
        ...

    @abstractmethod
    def delete_documents(self, document_ids: List[str]) -> bool: ...

    @abstractmethod
    def get_document_by_source(self, source: str) -> List[Document]:
        """Fetch all chunks belonging to a source file."""
        ...

    @abstractmethod
    def collection_stats(self) -> dict:
        """Return total document count, collection name, etc."""
        ...