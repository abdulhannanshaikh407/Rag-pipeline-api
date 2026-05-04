# RAG Pipeline Architecture

## System Overview

This RAG (Retrieval-Augmented Generation) pipeline is built with a modular, scalable architecture designed for production deployment. The system processes documents, stores them in vector databases, and answers user queries using LLMs with retrieved context.

## Pipeline Flow

### 1. Document Ingestion Pipeline

```
User Upload → Document Loader → Chunker → Embedder → Vector Store
     │              │              │           │            │
     └──────────────┴──────────────┴───────────┴────────────┘
                       Background Task (FastAPI)
```

#### Document Loader (`app/services/ingestion/document_loader.py`)
- Supports multiple file formats: PDF, TXT, DOCX
- Uses `pypdf` for PDF extraction
- Uses `python-docx` for Word documents
- Returns LangChain `Document` objects with metadata

#### Chunker (`app/services/ingestion/chunker.py`)
Two strategies available:
1. **Recursive Chunking** (default): Uses LangChain's `RecursiveCharacterTextSplitter`
   - Separators: `["\n\n", "\n", ". ", " ", ""]`
   - Preserves paragraph boundaries
   - Configurable `chunk_size` and `chunk_overlap`

2. **Semantic Chunking**: Groups sentences by embedding similarity
   - Uses sentence-transformers for embeddings
   - Cosine similarity threshold: 0.5
   - Better for conceptually coherent chunks

Both strategies add metadata: `chunk_index`, `chunk_total`, `char_start`, `char_end`

#### Embedder (`app/services/embedding/embedder.py`)
- **Providers**: OpenAI (`text-embedding-3-small`) or HuggingFace (`all-MiniLM-L6-v2`)
- **Caching**: Redis-based with SHA-256 keys
- **Retry Logic**: Exponential backoff via `tenacity`
- **Batch Support**: Handles up to 2048 inputs for OpenAI

### 2. Retrieval Pipeline

```
Query → Query Rewrite → Hybrid Retriever → Ranked Documents
         │                   │                    │
         └───────────────────┴────────────────────┘
                    Returns top-k results
```

#### Hybrid Retriever (`app/services/retrieval/retriever.py`)
Combines two search methods:
1. **Vector Search**: Embedding-based similarity search
   - Weight: configurable (default 0.7)
   - Uses configured vector store

2. **BM25 Keyword Search**: Traditional TF-IDF style ranking
   - Weight: configurable (default 0.3)
   - Works on raw text

Final score = `vector_weight * vector_score + bm25_weight * bm25_score`

#### Query Rewriting (`app/services/retrieval/query_rewriter.py`)
- Expands queries for better retrieval
- Enabled/disabled via `QUERY_REWRITING_ENABLED` setting

### 3. Generation Pipeline

```
Documents + Query → LLM Client → Streaming/Non-Streaming Response
        │              │                    │
        └──────────────┴────────────────────┘
                    Returns answer + sources
```

#### LLM Client (`app/services/generation/llm_client.py`)
- **Providers**: OpenAI or Anthropic
- **Streaming**: SSE (Server-Sent Events) support
- **Token Tracking**: Uses `tiktoken` for token counting
- **Model**: Configurable via `LLM_MODEL`

## Technical Decisions

### Why FastAPI?
- Native async support for handling concurrent requests
- Automatic OpenAPI/Swagger documentation
- Pydantic integration for type safety
- Easy middleware integration (auth, rate limiting, logging)

### Why LangChain?
- Standardized `Document` interface
- Battle-tested text splitters
- Easy to swap embedding models and vector stores

### Why Hybrid Search?
- Vector search excels at semantic similarity
- BM25 excels at exact keyword matching
- Combining both improves recall and precision

### Database Choice: SQLite (Async)
- Lightweight, no separate server needed
- `aiosqlite` for async operations
- Sufficient for user management and usage tracking
- Can be replaced with PostgreSQL for production scale

### Vector Store Options
1. **ChromaDB**: Local, persistent, easy setup (default)
2. **FAISS**: Facebook's efficient similarity search (local)
3. **Pinecone**: Managed cloud solution (scale)

## Data Models

### User (`app/db/models.py`)
```python
- id: int
- username: str (unique)
- email: str (unique)
- hashed_password: str
- api_key: str (unique, for API access)
- is_active: bool
- created_at: datetime
```

### UsageTracking
```python
- id: int
- user_id: int (FK)
- endpoint: str
- tokens_used: int
- timestamp: datetime
```

## Authentication & Security

### JWT Authentication
- Tokens signed with `SECRET_KEY` using HS256
- Configurable expiration via `ACCESS_TOKEN_EXPIRE_MINUTES`
- Claims: `sub` (username), `user_id`

### API Key Authentication
- Alternative to JWT
- Pass via `X-API-Key` header
- Generated on user registration

### Rate Limiting
- Per-user rate limits via `slowapi`
- Configurable: `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW`

## Scalability Considerations

### Horizontal Scaling
- Stateless API design (user state in DB)
- Redis for shared caching
- Docker-ready with health checks

### Performance Optimizations
- Background task processing for uploads
- Embedding caching in Redis
- BM25 index built once per query (consider persisting for production)

### Limitations & Future Improvements

1. **ChromaDB is single-instance**: For multi-instance deployment, use Pinecone or a shared Chroma server
2. **No document update/delete**: Currently only upload (add)
3. **BM25 index not persisted**: Rebuilt on each query
4. **No conversation history**: Each query is independent
5. **No document access control**: All docs accessible by all users (use `user_id` filter)
6. **Streaming usage tracking**: Uses `asyncio.create_task` (consider a task queue like Celery)

## File Structure

```
rag-pipeline/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── router.py          # Main RAG endpoints
│   │   │   └── auth.py            # Auth endpoints
│   │   └── middleware/
│   │       ├── auth.py            # JWT/API key validation
│   │       ├── logging.py         # Request logging
│   │       └── rate_limit.py      # Rate limiting
│   ├── core/
│   │   ├── config.py              # Pydantic settings
│   │   ├── logging.py             # Structlog setup
│   │   └── exceptions.py         # Custom exceptions
│   ├── db/
│   │   ├── database.py            # SQLAlchemy async setup
│   │   └── models.py              # DB models
│   ├── models/
│   │   └── requests.py            # Pydantic request models
│   └── services/
│       ├── ingestion/
│       │   ├── document_loader.py
│       │   └── chunker.py
│       ├── embedding/
│       │   └── embedder.py
│       ├── vectorstore/
│       │   ├── chroma_store.py
│       │   ├── faiss_store.py
│       │   └── pinecone_store.py
│       ├── retrieval/
│       │   ├── retriever.py
│       │   └── query_rewriter.py
│       └── generation/
│           └── llm_client.py
├── tests/
│   ├── unit/
│   └── integration/
└── data/                          # Gitignored
```
