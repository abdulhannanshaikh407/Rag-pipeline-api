"""
Pydantic v2 response models.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SourceCitation(BaseModel):
    filename: str
    page: Optional[int] = None
    chunk_index: int
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    excerpt: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    query: str
    rewritten_query: Optional[str] = None
    metadata: Dict[str, Any]


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int
    processing_time_ms: float
    status: str


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    upload_timestamp: datetime
    chunk_count: int
    file_size: int
    file_type: str


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    error: str
    code: str
    details: Optional[Dict[str, Any]] = None