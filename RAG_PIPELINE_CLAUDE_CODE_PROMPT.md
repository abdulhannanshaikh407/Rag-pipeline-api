# 🚀 Production RAG Pipeline — Claude Code Build Prompt

> **How to use:** Open Claude Code in your terminal (`claude`), paste this entire prompt, and let it scaffold the full system. Claude Code will create every file, install dependencies, and wire everything together.

---

## 🎯 MISSION

You are building a **complete, production-grade Retrieval-Augmented Generation (RAG) pipeline** from scratch. This system will be:

- Sold to clients as a productized AI solution
- Showcased on GitHub as a senior engineering portfolio piece
- Deployed to production (Docker + cloud-ready)

**This is NOT a prototype. Every decision must be production quality.**

---

## 📁 EXACT PROJECT STRUCTURE TO CREATE

Create this exact directory and file structure. Do not deviate:

```
rag-pipeline/
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py              # /upload, /delete routes
│   │   │   ├── query.py               # /query route
│   │   │   └── health.py              # /health route
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # API key middleware
│   │   │   └── rate_limit.py          # Rate limiting middleware
│   │   └── dependencies.py            # FastAPI dependency injection
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                  # Pydantic settings from env vars
│   │   ├── logging.py                 # Structured JSON logger
│   │   └── exceptions.py             # Custom exception classes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── document_loader.py     # PDF, TXT, DOCX loaders
│   │   │   ├── chunker.py             # Semantic + recursive chunking
│   │   │   └── metadata_extractor.py  # Source, page, date metadata
│   │   ├── embedding/
│   │   │   ├── __init__.py
│   │   │   └── embedder.py            # OpenAI / HuggingFace embeddings
│   │   ├── vectorstore/
│   │   │   ├── __init__.py
│   │   │   ├── chroma_store.py        # ChromaDB implementation
│   │   │   ├── faiss_store.py         # FAISS implementation
│   │   │   └── base.py                # Abstract vector store interface
│   │   ├── retrieval/
│   │   │   ├── __init__.py
│   │   │   ├── retriever.py           # Hybrid search (BM25 + vector)
│   │   │   └── query_rewriter.py      # LLM-based query rewriting
│   │   └── generation/
│   │       ├── __init__.py
│   │       ├── llm_client.py          # OpenAI + Claude unified client
│   │       ├── prompt_manager.py      # Prompt templates with versioning
│   │       └── rag_chain.py           # Full RAG chain with streaming
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py                # Pydantic request schemas
│   │   └── responses.py               # Pydantic response schemas
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py              # File handling helpers
│       ├── cache.py                   # Redis caching layer
│       └── storage.py                 # Local + S3 storage abstraction
├── frontend/
│   ├── app.py                         # Streamlit frontend
│   ├── components/
│   │   ├── chat.py                    # Chat interface component
│   │   ├── upload.py                  # File upload component
│   │   └── sources.py                 # Source citation display
│   └── utils.py                       # Frontend helpers
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures
│   ├── unit/
│   │   ├── test_chunker.py
│   │   ├── test_embedder.py
│   │   └── test_retriever.py
│   └── integration/
│       ├── test_api_ingest.py
│       ├── test_api_query.py
│       └── test_rag_chain.py
├── scripts/
│   ├── ingest_cli.py                  # CLI tool for bulk document ingestion
│   ├── evaluate.py                    # RAG evaluation script
│   └── seed_data.py                   # Load sample documents for demo
├── docker/
│   ├── Dockerfile.api                 # API service Dockerfile
│   ├── Dockerfile.frontend            # Streamlit frontend Dockerfile
│   └── nginx.conf                     # Nginx reverse proxy config
├── data/
│   ├── documents/                     # Uploaded documents (gitignored)
│   ├── vectorstore/                   # ChromaDB persistent storage
│   └── samples/                       # Sample docs for testing
├── docs/
│   └── architecture.md               # System architecture notes
├── .env.example                       # All required environment variables
├── .env                               # Actual env (gitignored)
├── .gitignore
├── docker-compose.yml                 # Full stack orchestration
├── docker-compose.dev.yml             # Dev overrides
├── requirements.txt                   # All Python dependencies pinned
├── requirements-dev.txt               # Dev/test dependencies
├── Makefile                           # Common commands
└── README.md                          # World-class README
```

---

## ⚙️ STEP 1 — ENVIRONMENT & CONFIGURATION

### `.env.example` — Create this first with ALL variables:

```env
# ── LLM Provider ──────────────────────────────────────────
LLM_PROVIDER=openai                    # openai | anthropic
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=gpt-4-turbo-preview          # or claude-3-opus-20240229
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2048

# ── Embeddings ────────────────────────────────────────────
EMBEDDING_PROVIDER=openai              # openai | huggingface
EMBEDDING_MODEL=text-embedding-3-small # or sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSIONS=1536

# ── Vector Store ──────────────────────────────────────────
VECTOR_STORE=chroma                    # chroma | faiss | pinecone
CHROMA_PERSIST_DIR=./data/vectorstore
PINECONE_API_KEY=
PINECONE_ENV=
PINECONE_INDEX_NAME=rag-index

# ── Storage ───────────────────────────────────────────────
STORAGE_BACKEND=local                  # local | s3
LOCAL_UPLOAD_DIR=./data/documents
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=
AWS_REGION=us-east-1

# ── API Security ──────────────────────────────────────────
API_KEY=your-secret-api-key-here
API_KEY_HEADER=X-API-Key

# ── Rate Limiting ─────────────────────────────────────────
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60                   # seconds

# ── Caching ───────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600                         # seconds

# ── Chunking ──────────────────────────────────────────────
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
CHUNKING_STRATEGY=recursive            # recursive | semantic

# ── Retrieval ─────────────────────────────────────────────
RETRIEVAL_TOP_K=5
HYBRID_SEARCH_ENABLED=true
BM25_WEIGHT=0.3
VECTOR_WEIGHT=0.7
QUERY_REWRITING_ENABLED=true

# ── App ───────────────────────────────────────────────────
APP_ENV=development                    # development | production
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=["http://localhost:8501"]
```

### `app/core/config.py` — Pydantic settings (full implementation):

```python
"""
Application configuration management.
All settings are loaded from environment variables with type validation.
"""
from functools import lru_cache
from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────
    llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=2048, ge=1, le=8192)

    # ── Embeddings ────────────────────────────────────────
    embedding_provider: Literal["openai", "huggingface"] = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # ── Vector Store ──────────────────────────────────────
    vector_store: Literal["chroma", "faiss", "pinecone"] = "chroma"
    chroma_persist_dir: str = "./data/vectorstore"
    pinecone_api_key: str = ""
    pinecone_env: str = ""
    pinecone_index_name: str = "rag-index"

    # ── Storage ───────────────────────────────────────────
    storage_backend: Literal["local", "s3"] = "local"
    local_upload_dir: str = "./data/documents"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = ""
    aws_region: str = "us-east-1"

    # ── API Security ──────────────────────────────────────
    api_key: str = "changeme"
    api_key_header: str = "X-API-Key"
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # ── Caching ───────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600

    # ── Chunking ──────────────────────────────────────────
    chunk_size: int = Field(default=1000, ge=100, le=8000)
    chunk_overlap: int = Field(default=200, ge=0, le=500)
    chunking_strategy: Literal["recursive", "semantic"] = "recursive"

    # ── Retrieval ─────────────────────────────────────────
    retrieval_top_k: int = Field(default=5, ge=1, le=20)
    hybrid_search_enabled: bool = True
    bm25_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    vector_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    query_rewriting_enabled: bool = True

    # ── App ───────────────────────────────────────────────
    app_env: Literal["development", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["http://localhost:8501", "http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — call this everywhere."""
    return Settings()
```

---

## 🔧 STEP 2 — ALL SERVICES (Full Implementations)

### `app/services/ingestion/document_loader.py`

Implement a `DocumentLoader` class with these exact methods:

```python
class DocumentLoader:
    """
    Loads documents from disk or bytes into LangChain Document objects.
    Supports: PDF (with page metadata), TXT, DOCX.
    """
    
    def load_file(self, file_path: str) -> List[Document]:
        """Route to correct loader based on file extension."""
        ...

    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Use PyMuPDF (fitz) for PDF loading.
        Each page = one Document with metadata:
          source, page_number, total_pages, file_name, file_size, created_at
        """
        ...

    def load_txt(self, file_path: str) -> List[Document]:
        """Load plain text. Detect encoding with chardet."""
        ...

    def load_docx(self, file_path: str) -> List[Document]:
        """Use python-docx. Extract paragraphs + tables."""
        ...

    def load_from_bytes(self, content: bytes, filename: str) -> List[Document]:
        """Save to temp file, load, then clean up."""
        ...
```

### `app/services/ingestion/chunker.py`

```python
class DocumentChunker:
    """
    Two chunking strategies:
    
    1. recursive: LangChain RecursiveCharacterTextSplitter
       - Splits on ["\n\n", "\n", ". ", " ", ""] in order
       - Preserves paragraph boundaries
    
    2. semantic: Group sentences by embedding similarity
       - Use sentence-transformers to embed each sentence
       - Merge sentences until cosine similarity drops below threshold
       - Better for conceptually coherent chunks
    
    Both strategies must:
    - Preserve ALL original document metadata
    - Add chunk_index, chunk_total, char_start, char_end to metadata
    - Return List[Document]
    """
    
    def chunk(self, documents: List[Document]) -> List[Document]: ...
    def _recursive_chunk(self, documents: List[Document]) -> List[Document]: ...
    def _semantic_chunk(self, documents: List[Document]) -> List[Document]: ...
```

### `app/services/embedding/embedder.py`

```python
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
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]: ...
    def embed_query(self, query: str) -> List[float]: ...
    def _batch_embed(self, texts: List[str], batch_size: int = 100) -> List[List[float]]: ...
```

### `app/services/vectorstore/base.py`

```python
from abc import ABC, abstractmethod

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
```

### `app/services/vectorstore/chroma_store.py`

```python
class ChromaVectorStore(BaseVectorStore):
    """
    ChromaDB implementation.
    - Use chromadb.PersistentClient for disk persistence
    - Collection name from config
    - Store embeddings + full metadata
    - Support metadata filters via Chroma's `where` clause
    - Handle collection creation idempotently
    """
```

### `app/services/retrieval/retriever.py`

```python
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
        ...
```

### `app/services/retrieval/query_rewriter.py`

```python
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
    
    def rewrite(self, query: str) -> RewrittenQuery: ...
```

### `app/services/generation/llm_client.py`

```python
class LLMClient:
    """
    Unified client for OpenAI and Anthropic APIs.
    
    OpenAI:
    - Use openai.AsyncOpenAI for async support
    - Support streaming via stream=True
    - Handle rate limits with tenacity retry
    
    Anthropic:
    - Use anthropic.AsyncAnthropic
    - Map messages format correctly
    - Support streaming
    
    Both must support:
    - generate(messages, stream=False) -> str
    - stream_generate(messages) -> AsyncIterator[str]  (yields tokens)
    - Token counting before request
    """
```

### `app/services/generation/prompt_manager.py`

```python
class PromptManager:
    """
    Manages prompt templates with versioning.
    
    Templates stored as class attributes (not files) for portability.
    Each template is a PromptTemplate(Jinja2) with:
    - name: str
    - version: str
    - template: str
    - required_vars: List[str]
    
    Core templates to implement:
    
    RAG_SYSTEM_PROMPT:
    \"\"\"
    You are a precise, helpful assistant. Answer questions ONLY using the provided context.
    If the context doesn't contain the answer, say "I don't have enough information to answer this."
    Always cite your sources using [Source: filename, Page: N] format.
    Never make up information. Be concise but complete.
    \"\"\"
    
    RAG_USER_PROMPT:
    \"\"\"
    Context:
    {context}
    
    Question: {question}
    
    Instructions: Answer based solely on the context above. Cite sources inline.
    \"\"\"
    
    QUERY_REWRITE_PROMPT:
    \"\"\"
    Rewrite the following question to be more specific and retrieval-friendly.
    Return ONLY the rewritten question, no explanation.
    Original: {query}
    \"\"\"
    """
```

### `app/services/generation/rag_chain.py`

```python
class RAGChain:
    """
    Orchestrates the full RAG pipeline end-to-end.
    
    Flow:
    1. [Optional] Rewrite query via QueryRewriter
    2. Retrieve top_k documents via HybridRetriever
    3. Format context string with source citations
    4. Build prompt via PromptManager
    5. Call LLMClient (streaming or not)
    6. Return RAGResponse with answer + sources + metadata
    
    RAGResponse fields:
    - answer: str
    - sources: List[SourceCitation]  (filename, page, chunk_index, relevance_score)
    - query: str
    - rewritten_query: str | None
    - retrieval_time_ms: float
    - generation_time_ms: float
    - total_tokens: int
    - model: str
    
    Guardrails:
    - If retrieved docs score < 0.3, prepend "Low confidence:" to answer
    - If no docs retrieved, return "I don't have information about this topic."
    - Never expose raw prompts in response
    
    Async streaming:
    - stream_query() must yield str tokens via AsyncGenerator
    - Accumulate full answer, then yield final RAGResponse as last item
    """
    
    async def query(self, request: QueryRequest) -> RAGResponse: ...
    async def stream_query(self, request: QueryRequest) -> AsyncGenerator[str, None]: ...
```

---

## 🌐 STEP 3 — FASTAPI APPLICATION

### `app/main.py`

```python
"""
FastAPI application factory with all middleware, routes, and lifecycle events.

Must include:
- Lifespan context manager (startup: init vector store, connect Redis; shutdown: cleanup)
- CORSMiddleware with origins from config
- AuthMiddleware (check X-API-Key header on all routes except /health)
- RateLimitMiddleware (sliding window in Redis, fallback to in-memory if Redis down)
- RequestLoggingMiddleware (log method, path, status, duration in JSON)
- Global exception handler (return structured JSON errors, never expose tracebacks in prod)
- Mount all routers with /api/v1 prefix
- OpenAPI docs at /docs (disabled in production)
"""
```

### `app/api/routes/ingest.py`

```python
"""
POST /api/v1/upload
- Accept: multipart/form-data with file field
- Supported: .pdf, .txt, .docx (validate extension AND mime type)
- Max file size: 50MB (configurable)
- Save to storage backend (local or S3)
- Run ingestion pipeline async (DocumentLoader → Chunker → Embedder → VectorStore)
- Return: { document_id, filename, chunks_created, processing_time_ms, status }
- Background task: delete temp file after processing

POST /api/v1/upload/batch
- Accept: List[UploadFile]
- Process each file, collect results
- Return: { results: List[UploadResult], total_files, successful, failed }

DELETE /api/v1/documents/{document_id}
- Remove all chunks with matching source from vector store
- Remove file from storage
- Return: { deleted, document_id, chunks_removed }

GET /api/v1/documents
- List all ingested documents with metadata
- Pagination: ?page=1&limit=20
- Return: { documents: List[DocumentInfo], total, page, limit }
"""
```

### `app/api/routes/query.py`

```python
"""
POST /api/v1/query
Request body:
{
  "question": "What is the refund policy?",
  "top_k": 5,                    # optional, default from config
  "filters": {"source": "policy.pdf"},  # optional metadata filter
  "stream": false,               # optional, default false
  "rewrite_query": true          # optional, default from config
}

Response (non-streaming):
{
  "answer": "The refund policy allows...",
  "sources": [
    {
      "filename": "policy.pdf",
      "page": 3,
      "chunk_index": 2,
      "relevance_score": 0.92,
      "excerpt": "...relevant text excerpt..."
    }
  ],
  "query": "What is the refund policy?",
  "rewritten_query": "refund policy terms and conditions",
  "metadata": {
    "retrieval_time_ms": 45,
    "generation_time_ms": 1200,
    "total_tokens": 1450,
    "model": "gpt-4-turbo-preview"
  }
}

For stream=true:
- Return StreamingResponse with media_type="text/event-stream"
- Yield: data: {"token": "..."}\n\n
- Final event: data: {"done": true, "sources": [...], "metadata": {...}}\n\n
"""
```

### `app/api/middleware/auth.py`

```python
"""
API Key Authentication Middleware.

- Read X-API-Key header (configurable header name)
- Compare against settings.api_key using secrets.compare_digest() (timing-safe)
- Exclude paths: ["/health", "/docs", "/openapi.json", "/redoc"]
- Return 401 with JSON body if invalid: {"error": "Invalid API key", "code": "UNAUTHORIZED"}
- Log failed auth attempts (IP, path, timestamp) — never log the key itself
"""
```

### `app/api/middleware/rate_limit.py`

```python
"""
Sliding Window Rate Limiter.

- Use Redis ZADD/ZRANGEBYSCORE for accurate sliding window
- Key: rate_limit:{api_key}:{window_start}
- If Redis unavailable: fall back to in-memory dict (per-process, not distributed)
- Return 429 with headers:
    X-RateLimit-Limit: 100
    X-RateLimit-Remaining: 45
    X-RateLimit-Reset: 1234567890
    Retry-After: 30
- Body: {"error": "Rate limit exceeded", "retry_after_seconds": 30}
"""
```

### `app/models/requests.py` and `app/models/responses.py`

```python
# requests.py — All Pydantic v2 request models with validators:
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: Optional[int] = Field(default=None, ge=1, le=20)
    filters: Optional[Dict[str, Any]] = None
    stream: bool = False
    rewrite_query: Optional[bool] = None

class UploadResponse(BaseModel): ...
class QueryResponse(BaseModel): ...
class SourceCitation(BaseModel): ...
class DocumentInfo(BaseModel): ...
class HealthResponse(BaseModel): ...
class ErrorResponse(BaseModel): ...
```

---

## 🖥️ STEP 4 — STREAMLIT FRONTEND

### `frontend/app.py`

```python
"""
Professional Streamlit Chat Interface.

Layout:
- Sidebar: File upload, document list, settings panel
- Main: Chat history, message input, source viewer

Features to implement:
1. File Upload (sidebar):
   - st.file_uploader supporting pdf/txt/docx
   - Show upload progress
   - Display list of ingested documents with delete button
   - Show chunk count per document

2. Chat Interface (main):
   - st.chat_message for user/assistant bubbles
   - Stream tokens as they arrive (requests with stream=True)
   - Show typing indicator while streaming

3. Source Citations (below each answer):
   - Expandable st.expander("📚 Sources (3)")
   - Show filename, page, relevance score, excerpt
   - Color-code by relevance (green > 0.8, yellow > 0.6, red < 0.6)

4. Settings Panel (sidebar):
   - top_k slider (1-10)
   - model selector
   - enable/disable query rewriting toggle

5. Session State:
   - Persist chat history across reruns
   - Store API key in session (not hardcoded)
   - Remember filter settings

API_URL = os.getenv("API_URL", "http://localhost:8000")
"""
```

---

## 🐳 STEP 5 — DOCKER CONFIGURATION

### `docker/Dockerfile.api`

```dockerfile
# Multi-stage build for minimal image size

# Stage 1: Dependencies
FROM python:3.11-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app

# Security: non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY app/ ./app/
COPY scripts/ ./scripts/

# Create data directories
RUN mkdir -p data/documents data/vectorstore && \
    chown -R appuser:appuser /app

USER appuser

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### `docker-compose.yml`

```yaml
version: '3.9'

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./data:/app/data          # Persist documents + vectorstore
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    command: redis-server --appendonly yes  # AOF persistence

volumes:
  redis_data:
```

---

## 📦 STEP 6 — REQUIREMENTS.TXT (Pinned versions)

```txt
# API Framework
fastapi==0.110.0
uvicorn[standard]==0.27.1
python-multipart==0.0.9

# Settings
pydantic==2.6.3
pydantic-settings==2.2.1

# LLM Providers
openai==1.13.3
anthropic==0.19.1

# LangChain (orchestration — chosen over LlamaIndex for:
# - Better hybrid search primitives
# - More active community
# - Superior streaming support
# - Easier custom chain composition)
langchain==0.1.11
langchain-openai==0.0.8
langchain-community==0.0.27
langchain-text-splitters==0.0.1

# Document Loading
pymupdf==1.23.26          # PDF loading (PyMuPDF / fitz)
python-docx==1.1.0        # DOCX loading
chardet==5.2.0             # Encoding detection

# Embeddings
sentence-transformers==2.5.1
torch==2.2.1               # Required by sentence-transformers

# Vector Stores
chromadb==0.4.24
faiss-cpu==1.7.4
pinecone-client==3.1.0

# Search
rank-bm25==0.2.2           # BM25 implementation

# Caching & Async
redis==5.0.1
aiofiles==23.2.1
httpx==0.27.0

# Retry Logic
tenacity==8.2.3

# Evaluation
ragas==0.1.7               # RAG evaluation metrics

# Logging
structlog==24.1.0

# Testing
pytest==8.0.2
pytest-asyncio==0.23.5
pytest-cov==4.1.0
httpx==0.27.0              # For async TestClient

# Frontend
streamlit==1.31.1

# Storage
boto3==1.34.51             # AWS S3

# Security
slowapi==0.1.9             # Rate limiting for FastAPI
```

---

## 🧪 STEP 7 — TESTING

### `tests/conftest.py`

```python
"""
Pytest fixtures:
- settings: Override config for tests (use fake API keys, in-memory stores)
- test_client: AsyncClient with TestTransport
- sample_pdf: Create a real PDF in /tmp for testing
- sample_txt: Simple text document
- mock_embedder: Returns deterministic fake embeddings (no API calls)
- mock_llm: Returns canned responses (no API calls)
- populated_vectorstore: Pre-loaded ChromaDB with 20 test chunks
"""
```

### `tests/unit/test_chunker.py`

```python
"""
Test DocumentChunker:
- test_recursive_chunk_respects_size: No chunk exceeds chunk_size
- test_recursive_chunk_has_overlap: Consecutive chunks share expected tokens
- test_chunk_preserves_metadata: source/page/filename survive chunking
- test_chunk_adds_chunk_index: chunk_index increments per document
- test_semantic_chunk_groups_related: Related sentences stay together
- test_empty_document: Handles gracefully
- test_very_large_document: 100k char doc chunks without OOM
"""
```

### `tests/integration/test_api_query.py`

```python
"""
Integration tests using TestClient + mock embedder/llm:
- test_query_returns_200: Basic happy path
- test_query_with_filters: Metadata filter reduces sources
- test_query_streaming: SSE stream yields tokens
- test_query_no_docs: Returns appropriate "no info" response
- test_query_invalid_request: Empty question returns 422
- test_query_missing_auth: Returns 401
- test_query_rate_limit: 101st request returns 429
"""
```

---

## 📊 STEP 8 — EVALUATION SYSTEM

### `scripts/evaluate.py`

```python
"""
RAG Evaluation using RAGAS metrics.

Evaluation dataset format (data/samples/eval_dataset.json):
[
  {
    "question": "What is the return policy?",
    "ground_truth": "Items can be returned within 30 days...",
    "context_document": "policy.pdf"
  }
]

Metrics to compute:
- faithfulness: Is the answer faithful to retrieved context? (0-1)
- answer_relevancy: Does the answer address the question? (0-1)
- context_precision: Are retrieved chunks relevant? (0-1)
- context_recall: Are all relevant chunks retrieved? (0-1)
- answer_correctness: Does answer match ground truth? (0-1)

Output: evaluation_results_{timestamp}.json + printed table

CLI:
python scripts/evaluate.py --dataset data/samples/eval_dataset.json --output results/
"""
```

---

## 📄 STEP 9 — WORLD-CLASS README.md

The README must include these exact sections:

```markdown
# 🔍 RAG Pipeline — Production-Grade Document Intelligence

[![Python](badge)] [![FastAPI](badge)] [![Docker](badge)] [![License](badge)]

## Overview
## ✨ Features (with checkmarks)
## 🏗️ Architecture

[ASCII diagram showing: Documents → Loader → Chunker → Embedder → VectorStore
                         Query → Rewriter → Retriever → LLM → Response]

## 🚀 Quick Start (5-minute setup)
## ⚙️ Configuration Reference (table of all env vars)
## 📡 API Reference (curl examples for every endpoint)
## 🖥️ Frontend Usage (screenshots placeholder)
## 🐳 Docker Deployment
## ☁️ Cloud Deployment
  ### AWS EC2
  ### AWS ECS (production)
  ### Render.com (simple)
  ### Railway
## 📊 Evaluation
## 🔒 Security
## 🗺️ Roadmap
## 🤝 Contributing
## 📜 License
```

---

## 🛠️ STEP 10 — MAKEFILE & CLI

### `Makefile`

```makefile
.PHONY: install dev test lint docker-up docker-down ingest evaluate

install:
	pip install -r requirements.txt -r requirements-dev.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	streamlit run frontend/app.py

test:
	pytest tests/ -v --cov=app --cov-report=html

lint:
	ruff check app/ tests/
	mypy app/

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

ingest:
	python scripts/ingest_cli.py --dir data/samples/

evaluate:
	python scripts/evaluate.py --dataset data/samples/eval_dataset.json

logs:
	docker-compose logs -f api
```

### `scripts/ingest_cli.py`

```python
"""
CLI for bulk document ingestion.

Usage:
  python scripts/ingest_cli.py --file document.pdf
  python scripts/ingest_cli.py --dir ./docs/ --recursive
  python scripts/ingest_cli.py --dir ./docs/ --recursive --clear-existing

Options:
  --file      Single file to ingest
  --dir       Directory to ingest (all supported files)
  --recursive Recurse into subdirectories
  --clear-existing  Clear vector store before ingesting
  --api-url   Override API URL (default: http://localhost:8000)
  --api-key   Override API key (default: from .env)

Progress: Use rich library for progress bars and status display.
"""
```

---

## 🚨 IMPLEMENTATION RULES — READ BEFORE WRITING ANY CODE

1. **Type hints everywhere** — Every function parameter and return type must be annotated
2. **Docstrings** — Every class and public method needs a docstring
3. **No hardcoding** — Every value comes from `get_settings()`
4. **Async first** — All I/O operations must be `async/await`
5. **Error handling** — Every external call wrapped in try/except, log errors with context
6. **Structured logging** — Use `structlog` with JSON output. Every log entry includes `request_id`, `service`, `duration_ms`
7. **Never expose secrets** — API keys, tracebacks, internal paths never in HTTP responses
8. **Graceful degradation** — If Redis is down, fall back to in-memory. If rewriter fails, use original query
9. **Idempotency** — Uploading the same file twice should update, not duplicate
10. **Factory pattern** — Use factory functions to create services (enables easy mocking in tests)

---

## 📋 BUILD ORDER (Follow Exactly)

Execute in this sequence to avoid import errors:

```
1.  Create project structure (all dirs + __init__.py files)
2.  Write requirements.txt → pip install -r requirements.txt
3.  Write .env.example → copy to .env → fill test values
4.  app/core/config.py
5.  app/core/logging.py
6.  app/core/exceptions.py
7.  app/models/requests.py + responses.py
8.  app/services/ingestion/document_loader.py
9.  app/services/ingestion/chunker.py
10. app/services/embedding/embedder.py
11. app/services/vectorstore/base.py + chroma_store.py + faiss_store.py
12. app/services/retrieval/retriever.py + query_rewriter.py
13. app/services/generation/llm_client.py + prompt_manager.py + rag_chain.py
14. app/utils/cache.py + storage.py + file_utils.py
15. app/api/middleware/auth.py + rate_limit.py
16. app/api/dependencies.py
17. app/api/routes/health.py + ingest.py + query.py
18. app/main.py
19. frontend/app.py + components/
20. tests/conftest.py + all test files
21. scripts/ingest_cli.py + evaluate.py + seed_data.py
22. docker/Dockerfile.api + Dockerfile.frontend + nginx.conf
23. docker-compose.yml + docker-compose.dev.yml
24. Makefile
25. README.md
26. Run: make test → fix any failures → make docker-up → test end-to-end
```

---

## ✅ DONE CRITERIA

The build is complete when:
- [ ] `make test` passes with >80% coverage
- [ ] `make docker-up` starts all 3 services (api, frontend, redis)
- [ ] `curl -H "X-API-Key: changeme" http://localhost:8000/health` returns `{"status":"healthy"}`
- [ ] Upload a PDF via Streamlit → ask a question → get a cited answer
- [ ] `python scripts/ingest_cli.py --dir data/samples/` works
- [ ] README is complete and accurate
- [ ] No hardcoded values anywhere in `app/`

---

*Built for production. Designed for scale. Ready to ship.*
