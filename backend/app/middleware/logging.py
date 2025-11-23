"""
Structured logging middleware.
"""

import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging."""

    async def dispatch(self, request: Request, call_next: Callable):
        """Log request and response with structured data."""
        start_time = time.time()

        # Extract request info
        request_info = {
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log response
            log_data = {
                **request_info,
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
            }

            if response.status_code >= 500:
                logger.error(json.dumps(log_data))
            elif response.status_code >= 400:
                logger.warning(json.dumps(log_data))
            else:
                logger.info(json.dumps(log_data))

            # Add process time header
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            process_time = time.time() - start_time
            log_data = {
                **request_info,
                "error": str(e),
                "process_time": f"{process_time:.3f}s",
            }
            logger.error(json.dumps(log_data), exc_info=True)
            raise
