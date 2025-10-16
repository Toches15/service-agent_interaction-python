"""
FastAPI application entry point.

This module contains the main FastAPI application instance with proper
configuration, middleware setup, and lifecycle management for production use.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import get_database_health
from app.models.responses import APIInfoResponse, HealthResponse

from app.api.v1.router import api_router
from app.config.cfg import settings
from app.core.database import configure_databases, db_registry
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    general_exception_handler,
    http_exception_handler,
)
from app.core.logging import get_logger, setup_logging
from app.core.middleware import RequestTrackingMiddleware
from app.dependencies import get_service_container

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifecycle events.

    This function handles startup and shutdown events for the FastAPI application,
    including automatic database initialization and cleanup.

    Args:
        _app: The FastAPI application instance (unused in base implementation).

    Yields:
        None: Control back to the application during its lifetime.
    """
    # Startup
    logger.info("Starting up FastAPI application...")

    try:
        # Configure and initialize databases
        configure_databases()
        await db_registry.connect_all()

        # Initialize application services
        service_container = get_service_container()
        await service_container.initialize_all()

        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down FastAPI application...")

    try:
        # Cleanup services
        service_container = get_service_container()
        await service_container.cleanup_all()

        # Cleanup databases
        await db_registry.disconnect_all()

        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    This factory function creates a FastAPI application with proper configuration,
    middleware, and error handling setup.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    fastapi_app = FastAPI(
        title=settings.app_name,
        description="A FastAPI application for Agno agents with comprehensive dependency injection and monitoring",
        version=settings.app_version,
        debug=settings.debug,
        docs_url=settings.docs_url if not settings.is_production else None,
        redoc_url=settings.redoc_url if not settings.is_production else None,
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "System",
                "description": "System information, health checks, and API metadata",
            },
            {
                "name": "Examples",
                "description": "Example endpoints demonstrating dependency injection patterns",
            },
        ],
    )

    # Add middleware
    fastapi_app.add_middleware(RequestTrackingMiddleware)

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Add exception handlers
    fastapi_app.add_exception_handler(AppException, app_exception_handler)
    fastapi_app.add_exception_handler(HTTPException, http_exception_handler)
    fastapi_app.add_exception_handler(Exception, general_exception_handler)

    # Include API routers
    fastapi_app.include_router(api_router)

    return fastapi_app


# Create the FastAPI application instance
app = create_app()


@app.get(
    "/",
    tags=["System"],
    summary="API Information",
    description="Get comprehensive API information including version, environment, and available resources",
    response_model=APIInfoResponse,
)
async def root() -> APIInfoResponse:
    """
    Root endpoint providing API information and available resources.

    Returns:
        dict[str, str | None]: API information, version, environment, and documentation links.
    """
    return APIInfoResponse(
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        api_version="v1",
        docs_url=settings.docs_url if not settings.is_production else None,
        redoc_url=settings.redoc_url if not settings.is_production else None,
        api_prefix=settings.api_v1_prefix,
    )


@app.get(
    "/system/health",
    tags=["System"],
    summary="Health Check",
    description="System health status endpoint for monitoring, load balancers, and uptime checks",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for monitoring, load balancers, and uptime checks.

    Returns:
        dict: Health status with timestamp and database health for monitoring systems.
    """
    # Get database health status
    db_health = await get_database_health()

    # Determine overall health
    overall_healthy = len(db_health) == 0 or all(db_health.values())

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": "running",
        "databases": db_health if db_health else {"status": "no databases configured"},
    }


if __name__ == "__main__":
    try:
        import uvicorn

        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.reload and settings.is_development,
            log_level=str(settings.log_level).lower(),
        )
    except ImportError:
        logger.error("uvicorn is not installed. Install it with: pip install uvicorn")
        raise
