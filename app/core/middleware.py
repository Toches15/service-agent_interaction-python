"""
Custom middleware for the application.

This module provides middleware for request tracking, timing,
and other cross-cutting concerns.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger, request_id_var

logger = get_logger(__name__)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking requests with unique IDs and timing.

    This middleware adds a unique request ID to each request and logs
    request timing information for monitoring and debugging.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with tracking and timing.

        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.

        Returns:
            Response: The response from the application.
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Set in context variable for automatic propagation
        request_id_var.set(request_id)

        # Start timing
        start_time = time.time()

        # Log request start
        logger.info("Request started: %s %s", request.method, request.url.path)

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        # Log request completion
        logger.info(
            "Request completed: %s %s [Status: %s] [Time: %.3fs]",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        return response
