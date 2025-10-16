"""
Tests for main application endpoints.

This module tests the core application functionality
including health checks and API information.
"""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test the root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "environment" in data
    assert "api_version" in data


def test_health_endpoint(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/system/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "uptime" in data


def test_api_v1_basic_example_endpoint(client: TestClient):
    """Test the API v1 basic example endpoint."""
    response = client.get("/api/v1/examples/basic")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "environment" in data
    assert "authenticated" in data


def test_protected_endpoint_without_auth(client: TestClient):
    """Test that protected endpoint requires authentication."""
    response = client.get("/api/v1/examples/protected")
    assert response.status_code == 401


def test_paginated_endpoint(client: TestClient):
    """Test the paginated list endpoint."""
    response = client.get("/api/v1/examples/paginated")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data


def test_paginated_endpoint_with_pagination(client: TestClient):
    """Test paginated endpoint with pagination parameters."""
    response = client.get("/api/v1/examples/paginated?skip=5&limit=10")
    assert response.status_code == 200

    data = response.json()
    assert data["skip"] == 5
    assert data["limit"] == 10
