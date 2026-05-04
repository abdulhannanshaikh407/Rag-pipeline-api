# RAG Pipeline API

A production-ready Retrieval-Augmented Generation (RAG) pipeline built with FastAPI, supporting multiple LLM providers and vector stores.

## Overview

This project implements a complete RAG system that allows users to:
- Upload documents (PDF, text, DOCX) for ingestion
- Query documents using natural language
- Receive AI-generated answers based on retrieved context

## Features

- **Multi-provider support**: Works with OpenAI and Anthropic for LLM, OpenAI and HuggingFace for embeddings
- **Hybrid search**: Combines vector search with BM25 for better retrieval
- **Multiple vector stores**: Supports ChromaDB, FAISS, and Pinecone
- **Authentication**: JWT and API key-based auth
- **Rate limiting**: Configurable rate limits per user
- **Caching**: Redis-based embedding cache
- **Streaming support**: Stream LLM responses for better UX
- **Query rewriting**: Improves retrieval with query expansion
- **Horizontal scaling**: Docker-ready with docker-compose

## Frontend

A futuristic React + Vite frontend ("Aether Engine") is included in `/frontend`.

### Prerequisites

- Node.js 20+
- npm 10+

- Python 3.11+
- Redis (optional, for caching)
- Docker (optional, for containerized deployment)

### Run Frontend Locally

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
# Open http://localhost:3000
```

### Full Stack with Docker

```bash
docker-compose up --build
# API: http://localhost:8000
# Frontend: http://localhost:3000
```

### Local Development (Backend)

1. Clone the repository:
```bash
git clone <repo-url>
cd rag-pipeline
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (copy from example):
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

6. Visit `http://localhost:8000/docs` for the Swagger UI.

### Docker Deployment

```bash
docker-compose up --build
```

## API Usage

### Authentication

Register a user and get an API key or JWT token:

```bash
# Register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "email": "user1@example.com", "password": "pass123"}'

# Login (get JWT)
curl -X POST "http://localhost:8000/auth/token" \
  -d "username=user1&password=pass123"
```

### Upload Documents

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@document.pdf"
```

### Query Documents

```bash
# Non-streaming
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'

# Streaming
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain the concept", "stream": true}'
```

## Configuration

All configuration is done via environment variables. See `.env.example` for all available options.

Key variables:
- `LLM_PROVIDER`: `openai` or `anthropic`
- `OPENAI_API_KEY`: Your OpenAI API key
- `EMBEDDING_PROVIDER`: `openai` or `huggingface`
- `VECTOR_STORE`: `chroma`, `faiss`, or `pinecone`
- `SECRET_KEY`: Secret for JWT signing (change in production!)

## Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# All tests
pytest -v
```

## Project Structure

```
rag-pipeline/
├── app/
│   ├── api/              # FastAPI routes and middleware
│   ├── core/             # Config, logging, exceptions
│   ├── db/               # Database models and session
│   ├── models/           # Pydantic request/response models
│   ├── services/         # Business logic
│   │   ├── ingestion/    # Document loading and chunking
│   │   ├── embedding/    # Embedding generation
│   │   ├── vectorstore/  # Vector database operations
│   │   ├── retrieval/    # Document retrieval
│   │   └── generation/   # LLM interaction
├── frontend/              # React + Vite frontend (Aether Engine)
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── lib/          # API client and utilities
│   │   └── App.tsx      # Main app component
│   ├── package.json      # Node.js dependencies
│   ├── vite.config.ts   # Vite configuration
│   └── Dockerfile.frontend
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── data/                 # Data storage (gitignored)
├── .env.example          # Example environment variables
├── docker-compose.yml    # Docker services
├── Dockerfile            # Container build
└── requirements.txt      # Python dependencies
```

## License

MIT

## Author

Built as a demonstration of production-ready RAG pipeline architecture.
