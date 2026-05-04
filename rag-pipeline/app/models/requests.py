"""
Pydantic v2 request models with validators.
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: Optional[int] = Field(default=None, ge=1, le=20)
    filters: Optional[Dict[str, Any]] = None
    stream: bool = False
    rewrite_query: Optional[bool] = None


class UploadRequest(BaseModel):
    # This is handled by FastAPI's File(...) in the route
    pass


class DeleteRequest(BaseModel):
    document_id: str = Field(..., min_length=1)


class HealthRequest(BaseModel):
    pass