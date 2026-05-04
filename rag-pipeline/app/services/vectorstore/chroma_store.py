"""
ChromaDB vector store implementation.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from app.services.vectorstore.base import BaseVectorStore
from app.core.config import get_settings
from app.core.logging import setup_logging
import structlog

logger = structlog.get_logger()


class ChromaVectorStore(BaseVectorStore):
    """
    ChromaDB implementation.
    - Use chromadb.PersistentClient for disk persistence
    - Collection name from config
    - Store embeddings + full metadata
    - Support metadata filters via Chroma's `where` clause
    - Handle collection creation idempotently
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = chromadb.PersistentClient(
            path=self.settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection_name = "rag_collection"
        self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Get existing collection or create new one."""
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info("Using existing ChromaDB collection", name=self.collection_name)
        except Exception:
            self.collection = self.client.create_collection(name=self.collection_name)
            logger.info("Created new ChromaDB collection", name=self.collection_name)

    def add_documents(self, documents: List[Document], embeddings: List[List[float]]) -> List[str]:
        """Add documents. Returns list of generated IDs."""
        if not documents:
            return []

        ids = [f"{doc.metadata.get('source', 'unknown')}_{i}_{hash(doc.page_content)}"
               for i, doc in enumerate(documents)]

        # Prepare metadatas for ChromaDB (ensure values are strings, numbers, or booleans)
        metadatas = []
        for doc in documents:
            meta = {}
            for k, v in doc.metadata.items():
                # ChromaDB only accepts str, int, float, bool, or None
                if isinstance(v, (str, int, float, bool)) or v is None:
                    meta[k] = v
                else:
                    meta[k] = str(v)  # convert to string
            metadatas.append(meta)

        try:
            self.collection.add(
                embeddings=embeddings,
                documents=[doc.page_content for doc in documents],
                metadatas=metadatas,
                ids=ids,
            )
            logger.info("Added documents to ChromaDB", count=len(documents))
            return ids
        except Exception as e:
            logger.error("Failed to add documents to ChromaDB", error=str(e))
            raise

    def similarity_search(self, query_embedding: List[float], top_k: int, filters: dict = None) -> List[Document]:
        """Return top_k most similar documents."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters,
                include=["documents", "metadatas", "distances"]
            )

            documents = []
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    # Ensure we have the original metadata as much as possible
                    # Note: ChromaDB may have converted some types, but we preserve what we can
                    documents.append(Document(
                        page_content=results['documents'][0][i],
                        metadata=metadata
                    ))
            return documents
        except Exception as e:
            logger.error("ChromaDB similarity search failed", error=str(e))
            raise

    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs."""
        try:
            self.collection.delete(ids=document_ids)
            logger.info("Deleted documents from ChromaDB", count=len(document_ids))
            return True
        except Exception as e:
            logger.error("Failed to delete documents from ChromaDB", error=str(e))
            return False

    def get_document_by_source(self, source: str) -> List[Document]:
        """Fetch all chunks belonging to a source file."""
        try:
            results = self.collection.get(
                where={"source": source},
                include=["documents", "metadatas"]
            )

            documents = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    documents.append(Document(
                        page_content=results['documents'][i],
                        metadata=metadata
                    ))
            return documents
        except Exception as e:
            logger.error("Failed to get documents by source from ChromaDB", error=str(e))
            return []

    def collection_stats(self) -> dict:
        """Return total document count, collection name, etc."""
        try:
            count = self.collection.count()
            return {
                "total_document_count": count,
                "collection_name": self.collection_name,
                "vector_store": "chroma"
            }
        except Exception as e:
            logger.error("Failed to get ChromaDB collection stats", error=str(e))
            return {
                "total_document_count": 0,
                "collection_name": self.collection_name,
                "vector_store": "chroma",
                "error": str(e)
            }