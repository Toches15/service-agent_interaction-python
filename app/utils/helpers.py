"""
General utility functions for common operations.

This module provides helper functions that are commonly needed
across different types of applications. Add your own utility
functions here as your project grows.
"""

from typing import Any


def deep_merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        dict1: First dictionary.
        dict2: Second dictionary (takes precedence).

    Returns:
        dict: Merged dictionary.
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def normalize_pagination(skip: int = 0, limit: int = 100, max_limit: int = 1000) -> dict[str, int]:
    """
    Normalize pagination parameters with safety limits.

    Args:
        skip: Number of items to skip.
        limit: Maximum number of items to return.
        max_limit: Maximum allowed limit to prevent abuse.

    Returns:
        dict: Normalized pagination parameters.
    """
    # Ensure skip is not negative
    skip = max(0, skip)
    # Cap limit to prevent abuse
    limit = min(max(1, limit), max_limit)

    return {"skip": skip, "limit": limit}


# Add your project-specific utility functions here:
#
# def your_custom_function():
#     """Your custom utility function."""
#     pass
