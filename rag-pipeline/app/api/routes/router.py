from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db, AsyncSessionLocal
from app.db.models import UsageTracking, User
from app.api.middleware.auth import get_current_user
from app.services.ingestion.document_loader import DocumentLoader
from app.services.ingestion.chunker import Chunker
from app.services.embedding.embedder import EmbeddingService
from app.services.vectorstore.chroma_store import ChromaVectorStore
from app.services.generation.llm_client import LLMClient
from app.services.retrieval.retriever import HybridRetriever
from app.core.config import get_settings
from app.core.logging import setup_logging
import structlog
from app.core.rate_limit import limiter
import tiktoken

logger = structlog.get_logger()
router = APIRouter()
settings = get_settings()

loader = DocumentLoader()
embedder = EmbeddingService()
vector_store = ChromaVectorStore()
retriever = HybridRetriever(vector_store, embedder)
llm = LLMClient()

def count_tokens(text: str) -> int:
    try:
        enc = tiktoken.encoding_for_model(settings.llm_model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

async def record_usage(db: AsyncSession, user_id: int, endpoint: str, tokens_used: int):
    usage = UsageTracking(user_id=user_id, endpoint=endpoint, tokens_used=tokens_used)
    db.add(usage)
    await db.commit()

def process_upload_background(content: bytes, filename: str, user_id: int):
    try:
        logger.info("Starting background upload processing", filename=filename, user_id=user_id)
        documents = loader.load_from_bytes(content, filename)
        
        # Inject user_id into metadata
        for doc in documents:
            doc.metadata["user_id"] = user_id

        chunker = Chunker()
        chunks = chunker.chunk(documents)
        texts = [chunk.page_content for chunk in chunks]
        
        embeddings = embedder.embed_texts(texts)
        vector_store.add_documents(chunks, embeddings)
        logger.info("Finished background upload processing", filename=filename, chunks=len(chunks), user_id=user_id)
    except Exception as e:
        logger.error("Background upload processing failed", error=str(e), filename=filename, user_id=user_id)

@router.post("/upload")
@limiter.limit(f"{settings.rate_limit_requests}/{settings.rate_limit_window}second")
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        content = await file.read()
        
        # We record the upload usage
        tokens_estimate = len(content) // 4
        await record_usage(db, current_user.id, "/upload", tokens_estimate)

        # Run embedding and chunking in background to keep API responsive
        background_tasks.add_task(process_upload_background, content, file.filename, current_user.id)
        
        return {"message": f"Processing {file.filename} in the background."}
    except Exception as e:
        logger.exception("Upload endpoint error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
@limiter.limit(f"{settings.rate_limit_requests}/{settings.rate_limit_window}second")
async def query(
    request: Request,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    question = payload.get("question", "")
    stream = payload.get("stream", False)
    
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    try:
        # Retrieve docs using threadpool since ChromaDB is sync
        filters = {"user_id": current_user.id}
        docs = await run_in_threadpool(retriever.retrieve, question, settings.retrieval_top_k, filters)
        
        context = "\n\n".join([d.page_content for d in docs])
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer based on the context provided."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
        
        input_tokens = count_tokens(context) + count_tokens(question)

        if stream:
            async def generate_and_track():
                output_text = ""
                try:
                    async for chunk in llm.generate_stream(messages):
                        output_text += chunk
                        yield f"data: {chunk}\n\n"
                finally:
                    # After stream is done, record usage
                    output_tokens = count_tokens(output_text)
                    # We can't await inside the sync generator block safely, but async generator is fine.
                    # Wait, background tasks shouldn't be added to stream response easily, but we can do it via a separate async task.
                    import asyncio
                    asyncio.create_task(record_usage_task(current_user.id, "/query", input_tokens + output_tokens))
                    
            return StreamingResponse(generate_and_track(), media_type="text/event-stream")
        else:
            answer = await llm.generate(messages)
            output_tokens = count_tokens(answer)
            await record_usage(db, current_user.id, "/query", input_tokens + output_tokens)
            return {"answer": answer, "sources": [d.metadata for d in docs]}
    except Exception as e:
        logger.error("Query failed", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))

async def record_usage_task(user_id: int, endpoint: str, tokens: int):
    """Record usage with a fresh database session to avoid closed session issues."""
    async with AsyncSessionLocal() as db:
        usage = UsageTracking(user_id=user_id, endpoint=endpoint, tokens_used=tokens)
        db.add(usage)
        await db.commit()
