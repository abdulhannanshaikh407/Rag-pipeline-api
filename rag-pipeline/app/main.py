from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.routes.router import router
from app.api.routes.auth import router as auth_router
from app.db.database import engine, Base
from app.core.rate_limit import limiter
from app.api.middleware.logging import LoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="RAG Pipeline API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(LoggingMiddleware)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(router)
@app.get("/")
def root():
    return {"status": "running", "message": "RAG Pipeline is up!"}

@app.get("/health")
def health():
    return {"status": "healthy"}