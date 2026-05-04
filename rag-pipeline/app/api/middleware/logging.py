import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import clear_contextvars, bind_contextvars

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        clear_contextvars()
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        bind_contextvars(request_id=request_id)
        
        response = await call_next(request)
        return response
