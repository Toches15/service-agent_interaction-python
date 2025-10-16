"""
API v1 router configuration.

This module sets up the main API router for version 1 endpoints
and includes all route modules. This is the central place where
all route modules are registered.
"""

from fastapi import APIRouter

from app.config import settings
from app.api.v1 import examples

# Create the main API router
api_router = APIRouter(prefix=settings.api_v1_prefix)

# Import and register route modules

# Register all route modules
api_router.include_router(examples.router)

# Add your route modules here as you create them:
#
# Step 1: Create your route module (e.g., app/api/v1/users.py)
# Step 2: Import and include it here:
#
# from app.api.v1 import users, auth, items, files
# api_router.include_router(users.router)
# api_router.include_router(auth.router)
# api_router.include_router(items.router)
# api_router.include_router(files.router)
#
# That's it! The main app will automatically include all registered routes.
