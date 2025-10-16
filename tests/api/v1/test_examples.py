"""
Tests for API v1 example endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestExampleEndpoints:
    """Test example API endpoints."""

    def test_basic_example_endpoint(self, client: TestClient):
        """Test basic example endpoint."""
        response = client.get("/api/v1/examples/basic")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "environment" in data
        assert "authenticated" in data
        assert data["authenticated"] is False  # No auth provided
        assert data["user_id"] is None

    def test_basic_example_response_structure(self, client: TestClient):
        """Test basic example response has correct structure."""
        response = client.get("/api/v1/examples/basic")
        data = response.json()

        required_fields = ["message", "environment", "authenticated", "user_id"]
        for field in required_fields:
            assert field in data

    def test_protected_endpoint_without_auth(self, client: TestClient):
        """Test protected endpoint requires authentication."""
        response = client.get("/api/v1/examples/protected")
        assert response.status_code == 401

        data = response.json()
        assert "message" in data
        assert data["message"] == "Authentication required"

    def test_protected_endpoint_with_mock_auth(self, client: TestClient):
        """Test protected endpoint with mock authentication."""
        headers = {"Authorization": "Bearer mock-token"}
        response = client.get("/api/v1/examples/protected", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "user" in data
        assert "environment" in data

    def test_paginated_endpoint_default_params(self, client: TestClient):
        """Test paginated endpoint with default parameters."""
        response = client.get("/api/v1/examples/paginated")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert "sort_by" in data
        assert "sort_order" in data
        assert "user_authenticated" in data

        # Check default values
        assert data["skip"] == 0
        assert data["limit"] == 100
        assert data["sort_by"] == "created_at"
        assert data["sort_order"] == "desc"

    def test_paginated_endpoint_custom_params(self, client: TestClient):
        """Test paginated endpoint with custom parameters."""
        response = client.get("/api/v1/examples/paginated?skip=10&limit=5&sort_by=name&sort_order=asc")
        assert response.status_code == 200

        data = response.json()
        assert data["skip"] == 10
        assert data["limit"] == 5
        assert data["sort_by"] == "name"
        assert data["sort_order"] == "asc"

    def test_paginated_endpoint_items_structure(self, client: TestClient):
        """Test paginated endpoint returns properly structured items."""
        response = client.get("/api/v1/examples/paginated?limit=5")
        assert response.status_code == 200

        data = response.json()
        items = data["items"]
        assert isinstance(items, list)
        assert len(items) <= 5

        if items:  # If there are items, check structure
            item = items[0]
            assert "id" in item
            assert "name" in item
            assert "created_at" in item

    # Note: Upload endpoint tests would go here when the endpoint is implemented

    @pytest.mark.parametrize("endpoint", ["/api/v1/examples/basic", "/api/v1/examples/paginated"])
    def test_endpoints_have_request_tracking(self, client: TestClient, endpoint: str):
        """Test that endpoints include request tracking headers."""
        response = client.get(endpoint)
        assert response.status_code == 200

        # Check for request tracking headers
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers

        # Validate header values
        request_id = response.headers["X-Request-ID"]
        process_time = response.headers["X-Process-Time"]

        assert len(request_id) > 0
        assert float(process_time) >= 0
