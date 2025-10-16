"""
Base service classes and interfaces.

This module provides base classes and interfaces for implementing
business logic services with consistent patterns.
"""

from abc import ABC, abstractmethod
from typing import Any

from app.config import Settings
from app.core.logging import get_logger


class BaseService:
    """
    Base class for stateless business services.

    Use this for services that don't need initialization/cleanup:
    - Pure business logic (calculations, transformations)
    - Simple API wrappers that create connections per request
    - Stateless utilities and formatters

    These services are created once and reused without lifecycle management.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)


class StatefulService(BaseService, ABC):
    """
    Abstract base for services that require lifecycle management.

    Use this for services that need initialization/cleanup like:
    - External API clients with connection pools
    - Cache services with persistent connections
    - Message queue services
    - Database connections (though we handle those separately)
    """

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the stateful service.

        Called automatically during application startup.
        Use this to establish connections, load resources, etc.
        """

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Cleanup the stateful service.

        Called automatically during application shutdown.
        Use this to close connections, save state, etc.
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the stateful service is healthy.

        Called by the health check endpoint.

        Returns:
            bool: True if service is healthy, False otherwise.
        """


# Example service interfaces (create separate files for complex interfaces)
class CacheServiceInterface(ABC):
    """Interface for cache services."""

    @abstractmethod
    async def get(self, key: str) -> Any:
        """Get value from cache."""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache."""


# Service creation examples (DO NOT implement - just documentation):
#
# 1. STATELESS SERVICE (No initialization needed):
#
# class LLMService(BaseService):
#     """OpenAI/LLM service for text generation."""
#
#     async def generate_text(self, prompt: str) -> str:
#         # Uses self.settings.openai_api_key
#         # Creates HTTP client per request
#         async with httpx.AsyncClient() as client:
#             # Make API call
#             pass
#
# 2. STATEFUL SERVICE (Needs initialization):
#
# class RedisService(StatefulService, CacheServiceInterface):
#     """Redis cache service with persistent connection."""
#
#     def __init__(self, settings: Settings):
#         super().__init__(settings)
#         self.redis_client = None
#
#     async def initialize(self):
#         import redis.asyncio as redis
#         self.redis_client = redis.from_url(self.settings.redis_url)
#         await self.redis_client.ping()  # Test connection
#
#     async def cleanup(self):
#         if self.redis_client:
#             await self.redis_client.close()
#
#     async def health_check(self) -> bool:
#         try:
#             await self.redis_client.ping()
#             return True
#         except:
#             return False
#
# 3. BUSINESS LOGIC SERVICE (No initialization):
#
# class CalculationService(BaseService):
#     """Pure business logic service."""
#
#     def calculate_tax(self, amount: float, rate: float) -> float:
#         return amount * rate
#
#     async def complex_calculation(self, data: dict) -> dict:
#         # Pure business logic, no external dependencies
#         pass
