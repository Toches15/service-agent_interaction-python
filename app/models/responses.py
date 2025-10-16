"""
Response models for API documentation and validation.

This module defines Pydantic models for API responses to improve
Swagger documentation and provide type safety.
"""

from typing import Any

from pydantic import BaseModel, Field


class APIInfoResponse(BaseModel):
    """API information response model."""

    name: str = Field(..., description="API name")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Current environment")
    api_version: str = Field(..., description="API version identifier")
    docs_url: str | None = Field(None, description="Swagger documentation URL")
    redoc_url: str | None = Field(None, description="ReDoc documentation URL")
    api_prefix: str = Field(..., description="API prefix path")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Health status", json_schema_extra={"example": "healthy"})
    timestamp: str = Field(..., description="Current timestamp in ISO format")
    uptime: str = Field(..., description="Uptime status", json_schema_extra={"example": "running"})


class ExampleResponse(BaseModel):
    """Example endpoint response model."""

    message: str = Field(..., description="Response message")
    environment: str = Field(..., description="Current environment")
    authenticated: bool = Field(..., description="Whether user is authenticated")
    user_id: str | None = Field(None, description="User ID if authenticated")


class ProtectedResponse(BaseModel):
    """Protected endpoint response model."""

    message: str = Field(..., description="Response message")
    user: dict[str, Any] = Field(..., description="Authenticated user information")
    environment: str = Field(..., description="Current environment")


class ItemModel(BaseModel):
    """Individual item model."""

    id: int = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    created_at: str = Field(..., description="Creation timestamp")


class ItemsListResponse(BaseModel):
    """Items list response with pagination."""

    items: list[ItemModel] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")
    sort_by: str = Field(..., description="Sort field")
    sort_order: str = Field(..., description="Sort order")
    user_authenticated: bool = Field(..., description="Whether user is authenticated")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    request_id: str | None = Field(None, description="Request ID for tracking")
