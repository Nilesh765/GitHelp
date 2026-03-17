from uuid import uuid4
import time
import logging
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import correlation_id_var

logger = logging.getLogger(__name__)

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:

        correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
        correlation_id_var.set(correlation_id)
        request.state.correlation_id = correlation_id

        start_time = time.time()

        response = await call_next(request)
        
        duration_ms = round((time.time() - start_time) * 1000)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Duration-Time"] = f"{duration_ms:.2f}ms"

        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "correlation_id": correlation_id,
            }
        )
        return response