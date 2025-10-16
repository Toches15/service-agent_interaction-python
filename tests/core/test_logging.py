"""
Tests for logging configuration and functionality.
"""

import logging
from unittest.mock import patch

import pytest

from app.core.logging import get_logger, setup_logging, request_id_var


class TestLogging:
    """Test logging configuration and functionality."""

    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a proper logger instance."""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_setup_logging_configures_root_logger(self):
        """Test that setup_logging properly configures the root logger."""
        with patch("app.core.logging.get_settings") as mock_settings:
            mock_settings.return_value.log_level = "INFO"
            mock_settings.return_value.log_format = "text"
            mock_settings.return_value.environment = "test"

            setup_logging()

            root_logger = logging.getLogger()
            assert root_logger.level == logging.INFO

    def test_request_id_context_variable(self):
        """Test request ID context variable functionality."""
        # Test default value
        assert request_id_var.get() is None

        # Test setting and getting value
        test_id = "test-request-123"
        request_id_var.set(test_id)
        assert request_id_var.get() == test_id

    @pytest.mark.asyncio
    async def test_request_id_propagation_in_async_context(self):
        """Test that request ID propagates correctly in async context."""
        test_id = "async-test-456"
        request_id_var.set(test_id)

        # Simulate async operation
        import asyncio

        await asyncio.sleep(0.001)

        # Request ID should still be available
        assert request_id_var.get() == test_id
