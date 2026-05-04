"""
Custom exception classes for the RAG pipeline.
"""
from typing import Any, Dict, Optional


class RAGException(Exception):
    """Base exception for RAG pipeline."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.message,
            "code": self.error_code,
            "details": self.details,
        }


class DocumentProcessingError(RAGException):
    """Error during document loading, chunking, or embedding."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="DOCUMENT_PROCESSING_ERROR",
            status_code=422,
            details=details,
        )


class VectorStoreError(RAGException):
    """Error interacting with the vector store."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="VECTOR_STORE_ERROR",
            status_code=500,
            details=details,
        )


class EmbeddingError(RAGException):
    """Error generating embeddings."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="EMBEDDING_ERROR",
            status_code=500,
            details=details,
        )


class LLMError(RAGException):
    """Error during LLM generation."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="LLM_ERROR",
            status_code=500,
            details=details,
        )


class InvalidAPIKeyError(RAGException):
    """Error for invalid API key."""

    def __init__(self):
        super().__init__(
            message="Invalid API key",
            error_code="UNAUTHORIZED",
            status_code=401,
        )


class RateLimitError(RAGException):
    """Error when rate limit is exceeded."""

    def __init__(self, retry_after: int):
        super().__init__(
            message="Rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after_seconds": retry_after},
        )


class ConfigurationError(RAGException):
    """Error in configuration."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500,
        )