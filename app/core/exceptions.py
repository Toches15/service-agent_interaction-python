"""
Custom exceptions and error handlers for the application.

This module defines custom exception classes and FastAPI exception handlers
for consistent error responses across the application.
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger(__name__)


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    message: str
    status_code: int
    request_id: str | None = None


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error exception."""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class NotFoundError(AppException):
    """Resource not found exception."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle custom application exceptions.

    Args:
        request: The FastAPI request object.
        exc: The application exception.

    Returns:
        JSONResponse: Formatted error response.
    """
    logger.error("Application error: %s", exc.message, exc_info=exc)

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.message,
            status_code=exc.status_code,
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.

    Args:
        request: The FastAPI request object.
        exc: The HTTP exception.

    Returns:
        JSONResponse: Formatted error response.
    """
    logger.warning("HTTP error %s: %s", exc.status_code, exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPException",
            message=str(exc.detail),
            status_code=exc.status_code,
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: The FastAPI request object.
        exc: The unexpected exception.

    Returns:
        JSONResponse: Formatted error response.
    """
    logger.error("Unexpected error: %s", str(exc), exc_info=exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(),
    )
