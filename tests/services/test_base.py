"""
Tests for base service classes.
"""

import pytest

from app.services.base import BaseService, StatefulService
from app.config import get_settings


class MockStatefulService(StatefulService):
    """Mock stateful service for testing."""

    def __init__(self, settings):
        super().__init__(settings)
        self.initialized = False
        self.cleaned_up = False
        self.healthy = True

    async def initialize(self):
        self.initialized = True

    async def cleanup(self):
        self.cleaned_up = True

    async def health_check(self) -> bool:
        return self.healthy


class TestBaseService:
    """Test base service functionality."""

    def test_base_service_initialization(self):
        """Test BaseService initialization."""
        settings = get_settings()
        service = BaseService(settings)

        assert service.settings == settings
        assert hasattr(service, "logger")
        assert service.logger.name == "BaseService"

    def test_base_service_logger_name(self):
        """Test that logger name matches class name."""
        settings = get_settings()
        service = BaseService(settings)

        assert service.logger.name == "BaseService"


class TestStatefulService:
    """Test stateful service functionality."""

    def test_stateful_service_initialization(self):
        """Test StatefulService initialization."""
        settings = get_settings()
        service = MockStatefulService(settings)

        assert service.settings == settings
        assert hasattr(service, "logger")
        assert service.initialized is False
        assert service.cleaned_up is False

    @pytest.mark.asyncio
    async def test_stateful_service_lifecycle(self):
        """Test complete stateful service lifecycle."""
        settings = get_settings()
        service = MockStatefulService(settings)

        # Initial state
        assert service.initialized is False
        assert service.cleaned_up is False

        # Initialize
        await service.initialize()
        assert service.initialized is True

        # Health check
        health = await service.health_check()
        assert health is True

        # Cleanup
        await service.cleanup()
        assert service.cleaned_up is True

    @pytest.mark.asyncio
    async def test_stateful_service_health_check_unhealthy(self):
        """Test health check when service is unhealthy."""
        settings = get_settings()
        service = MockStatefulService(settings)
        service.healthy = False

        health = await service.health_check()
        assert health is False

    def test_stateful_service_abstract_methods(self):
        """Test that StatefulService enforces abstract methods."""
        settings = get_settings()

        # Should not be able to instantiate StatefulService directly
        with pytest.raises(TypeError):
            StatefulService(settings)

    def test_mock_service_logger_name(self):
        """Test that mock service has correct logger name."""
        settings = get_settings()
        service = MockStatefulService(settings)

        assert service.logger.name == "MockStatefulService"
