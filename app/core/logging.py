"""
Logging configuration for the application.

This module provides centralized logging setup with proper formatting,
handlers, and configuration based on environment settings.
"""

import contextvars
import json
import logging
import sys
from datetime import datetime

from app.config import get_settings

# Import request ID context variable
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default=None)


class RequestContextFormatter(logging.Formatter):
    """Formatter that automatically adds request ID to all log messages."""

    def format(self, record: logging.LogRecord) -> str:
        """Add request ID to log record automatically."""
        # Get request ID from context variable
        request_id = request_id_var.get()
        record.request_id = request_id  # Can be None for non-request logs

        return super().format(record)


class TextFormatter(RequestContextFormatter):
    """Text formatter that conditionally shows request ID."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with conditional request ID."""
        # First, let parent add request ID
        super().format(record)

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        # Build log message with conditional request ID
        if hasattr(record, "request_id") and record.request_id:
            return f"{timestamp} - {record.name} - {record.levelname} - [{record.request_id}] - {record.getMessage()}"
        else:
            return f"{timestamp} - {record.name} - {record.levelname} - {record.getMessage()}"


class JSONFormatter(RequestContextFormatter):
    """JSON formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with automatic request ID."""
        # First, let parent add request ID
        super().format(record)

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
        }

        # Add request ID if available (skip if None)
        if hasattr(record, "request_id") and record.request_id:
            log_entry["request_id"] = record.request_id

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
                "request_id",
            }:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


def setup_logging() -> None:
    """
    Configure application logging.

    Sets up logging with appropriate level, format, and handlers
    based on the current environment configuration.
    """
    settings = get_settings()

    # Use JSON in production, text in development
    use_json = str(settings.log_format).lower() == "json"

    # Create formatter with automatic request ID
    if use_json:
        formatter = JSONFormatter()
    else:
        # Custom text formatter that only shows request ID when present
        formatter = TextFormatter()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, str(settings.log_level).upper()))
    root_logger.handlers.clear()  # Clear any existing handlers
    root_logger.addHandler(console_handler)

    # Reduce third-party noise in production
    if settings.environment == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {settings.environment} environment")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
