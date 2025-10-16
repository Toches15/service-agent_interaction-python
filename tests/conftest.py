"""
Pytest configuration and fixtures.

This module provides common test fixtures and configuration
for the test suite.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """
    Test client fixture.

    Returns:
        TestClient: FastAPI test client.
    """
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """
    Mock settings fixture for testing.

    Returns:
        dict: Mock settings configuration.
    """
    return {
        "environment": "testing",
        "debug": True,
        "secret_key": "test-secret-key-for-testing-only",
        "database_url": "sqlite:///./test.db",
    }


# Add more fixtures as needed:
# @pytest.fixture
# async def async_client():
#     """Async test client fixture."""
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         yield ac
#
#
# @pytest.fixture
# async def db_session():
#     """Database session fixture for testing."""
#     # Setup test database session
#     pass
