"""
Application dependencies for dependency injection.

This module provides centralized dependency management for FastAPI,
including database sessions, authentication, logging, and other shared services.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.cfg import Settings, get_settings
from app.core.database import db_registry, get_main_db_session, get_main_database
from app.core.logging import get_logger
from app.utils.helpers import normalize_pagination

# Security scheme for JWT authentication (when implemented)
security = HTTPBearer(auto_error=False)

logger = get_logger(__name__)


# Configuration Dependencies
def get_app_settings() -> Settings:
    """
    Get application settings dependency.

    Returns:
        Settings: Application configuration instance.
    """
    return get_settings()


# Logging Dependencies
# Note: LoggerDep is no longer needed since request IDs are automatic
# Just use: logger = get_logger(__name__) in any module


# Authentication Dependencies (placeholder for future implementation)
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
) -> dict | None:
    """
    Get current authenticated user (placeholder implementation).

    Args:
        credentials: HTTP authorization credentials.

    Returns:
        dict | None: User information or None if not authenticated.

    Raises:
        HTTPException: If authentication is required but not provided.
    """
    if credentials is None:
        return None

    # Placeholder for JWT token validation
    # In a real implementation, you would:
    # 1. Decode and validate the JWT token
    # 2. Extract user information from the token
    # 3. Optionally fetch additional user data from database

    # For now, return a mock user
    return {"id": "user123", "username": "testuser", "email": "test@example.com"}


async def require_authentication(
    current_user: Annotated[dict | None, Depends(get_current_user)],
) -> dict:
    """
    Require authentication for protected endpoints.

    Args:
        current_user: Current user from get_current_user dependency.

    Returns:
        dict: Authenticated user information.

    Raises:
        HTTPException: If user is not authenticated.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


# Database Dependencies
async def get_database_session():
    """
    Get main database session dependency (SQLAlchemy).

    Yields:
        Database session for the main database.

    Raises:
        ValueError: If main database is not configured or not SQLAlchemy.
    """
    try:
        async for session in get_main_db_session():
            yield session
    except ValueError:
        # Database not configured or not SQLAlchemy - this is fine
        yield None


def get_database():
    """
    Get main database dependency (databases library or MongoDB).

    Returns:
        Database instance or None if not configured.
    """
    try:
        return get_main_database()
    except ValueError:
        # Database not configured - this is fine
        return None


async def get_database_health() -> dict[str, bool]:
    """
    Get health status of all configured databases.

    Returns:
        dict: Database name to health status mapping.
    """
    return await db_registry.health_check_all()


# Service Dependencies
class ServiceContainer:
    """
    Container for application services with lazy loading.

    This class manages all business logic services and provides them
    as dependencies throughout the application. Services are loaded
    lazily to improve startup performance.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)

        # Private service instances (lazy-loaded)
        self._services: dict[str, object] = {}
        self._initialized = False

    async def initialize_all(self) -> None:
        """Initialize all registered services."""
        if self._initialized:
            return

        self.logger.info("Initializing application services...")

        # Initialize services that need async setup
        for service_name, service in self._services.items():
            if hasattr(service, "initialize"):
                try:
                    await service.initialize()
                    self.logger.info(f"Service '{service_name}' initialized successfully")
                except Exception as e:
                    self.logger.error(f"Failed to initialize service '{service_name}': {e}")

        self._initialized = True
        self.logger.info("Service initialization complete")

    async def cleanup_all(self) -> None:
        """Cleanup all services."""
        if not self._initialized:
            return

        self.logger.info("Cleaning up application services...")

        for service_name, service in self._services.items():
            if hasattr(service, "cleanup"):
                try:
                    await service.cleanup()
                    self.logger.info(f"Service '{service_name}' cleaned up successfully")
                except Exception as e:
                    self.logger.error(f"Failed to cleanup service '{service_name}': {e}")

        self._initialized = False
        self.logger.info("Service cleanup complete")

    def register_service(self, name: str, service: object) -> None:
        """Register a service instance."""
        self._services[name] = service

    def get_service(self, name: str) -> object:
        """Get a service by name."""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")
        return self._services[name]

    # Example service properties (uncomment and implement as needed)
    #
    # @property
    # def email_service(self) -> EmailServiceInterface:
    #     """Get email service instance."""
    #     if 'email' not in self._services:
    #         from app.services.email import EmailService
    #         self._services['email'] = EmailService(self.settings)
    #     return self._services['email']
    #
    # @property
    # def cache_service(self) -> CacheServiceInterface:
    #     """Get cache service instance."""
    #     if 'cache' not in self._services:
    #         from app.services.cache import RedisService
    #         self._services['cache'] = RedisService(self.settings)
    #     return self._services['cache']
    #
    # @property
    # def notification_service(self):
    #     """Get notification service instance."""
    #     if 'notification' not in self._services:
    #         from app.services.notification import NotificationService
    #         self._services['notification'] = NotificationService(self.settings)
    #     return self._services['notification']


@lru_cache()
def get_service_container() -> ServiceContainer:
    """
    Get service container dependency.

    Returns:
        ServiceContainer: Container with all application services.
    """
    settings = get_settings()
    return ServiceContainer(settings)


# Common Query Parameters
class CommonQueryParams:
    """Common query parameters for list endpoints."""

    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        # Use the utility function for safe pagination
        pagination = normalize_pagination(skip, limit)
        self.skip = pagination["skip"]
        self.limit = pagination["limit"]
        self.sort_by = sort_by
        self.sort_order = sort_order


# Type aliases for common dependencies
SettingsDep = Annotated[Settings, Depends(get_app_settings)]
ServicesDep = Annotated[ServiceContainer, Depends(get_service_container)]
CurrentUserDep = Annotated[dict | None, Depends(get_current_user)]
AuthenticatedUserDep = Annotated[dict, Depends(require_authentication)]
CommonQueryDep = Annotated[CommonQueryParams, Depends(CommonQueryParams)]
DatabaseSessionDep = Annotated[object, Depends(get_database_session)]
DatabaseDep = Annotated[object, Depends(get_database)]
