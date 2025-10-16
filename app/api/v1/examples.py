"""
Example API endpoints for demonstration.

This module shows how to create a separate route module and demonstrates
various dependency injection patterns. Use this as a reference when
creating your own route modules.
"""

from fastapi import APIRouter

from app.dependencies import (
    AuthenticatedUserDep,
    CommonQueryDep,
    CurrentUserDep,
    ServicesDep,
    SettingsDep,
)
from app.core.logging import get_logger
from app.models.responses import (
    ExampleResponse,
    ItemsListResponse,
    ProtectedResponse,
)


# Get logger and test automatic request ID
logger = get_logger(__name__)

# Create router for example endpoints
router = APIRouter(prefix="/examples", tags=["Examples"])


@router.get(
    "/basic",
    summary="Basic Example",
    description="Demonstrates dependency injection patterns with optional authentication",
    response_model=ExampleResponse,
)
async def basic_example(
    app_settings: SettingsDep,
    current_user: CurrentUserDep,
    services: ServicesDep,
) -> ExampleResponse:
    """
    Basic example endpoint showing dependency injection.

    Args:
        app_settings: Application settings dependency.
        current_user: Current user (optional authentication).
        services: Service container dependency.

    Returns:
        ExampleResponse: Example response with user context.
    """
    # Services container available for future enhancements
    _ = services

    logger.info("Basic example endpoint called")
    return ExampleResponse(
        message="This is a basic example endpoint",
        environment=app_settings.environment,
        authenticated=current_user is not None,
        user_id=current_user.get("id") if current_user else None,
    )


@router.get(
    "/protected",
    summary="Protected Example",
    description="Requires authentication - demonstrates required user dependency injection",
    response_model=ProtectedResponse,
)
async def protected_example(
    user: AuthenticatedUserDep,
    app_settings: SettingsDep,
) -> ProtectedResponse:
    """
    Protected endpoint requiring authentication.

    Args:
        user: Authenticated user dependency.
        app_settings: Application settings dependency.

    Returns:
        ProtectedResponse: Protected resource response.
    """
    return ProtectedResponse(
        message="This is a protected example endpoint",
        user=user,
        environment=app_settings.environment,
    )


@router.get(
    "/paginated",
    summary="Paginated Example",
    description="Get paginated list with sorting and optional user context",
    response_model=ItemsListResponse,
)
async def paginated_example(
    query_params: CommonQueryDep,
    user: CurrentUserDep,
) -> ItemsListResponse:
    """
    Paginated list example with sorting.

    Args:
        query_params: Common query parameters (skip, limit, sort).
        user: Current user (optional).

    Returns:
        ItemsListResponse: Paginated list response.
    """
    # Mock data - replace with actual database query
    items = [{"id": i, "name": f"Item {i}", "created_at": "2024-01-01T00:00:00Z"} for i in range(1, 21)]

    # Apply pagination
    start = query_params.skip
    end = start + query_params.limit
    paginated_items = items[start:end]

    return ItemsListResponse(
        items=paginated_items,
        total=len(items),
        skip=query_params.skip,
        limit=query_params.limit,
        sort_by=query_params.sort_by,
        sort_order=query_params.sort_order,
        user_authenticated=user is not None,
    )
