"""
Tests for utility helper functions.
"""

import pytest

from app.utils.helpers import normalize_pagination


class TestHelpers:
    """Test utility helper functions."""

    def test_normalize_pagination_valid_values(self):
        """Test pagination normalization with valid values."""
        result = normalize_pagination(10, 20)
        assert result == {"skip": 10, "limit": 20}

    def test_normalize_pagination_negative_skip(self):
        """Test pagination normalization with negative skip."""
        result = normalize_pagination(-5, 20)
        assert result == {"skip": 0, "limit": 20}

    def test_normalize_pagination_zero_limit(self):
        """Test pagination normalization with zero limit."""
        result = normalize_pagination(10, 0)
        assert result == {"skip": 10, "limit": 1}

    def test_normalize_pagination_negative_limit(self):
        """Test pagination normalization with negative limit."""
        result = normalize_pagination(10, -5)
        assert result == {"skip": 10, "limit": 1}

    def test_normalize_pagination_limit_too_high(self):
        """Test pagination normalization with limit exceeding maximum."""
        result = normalize_pagination(10, 2000)  # Exceeds default max of 1000
        assert result == {"skip": 10, "limit": 1000}

    def test_normalize_pagination_default_values(self):
        """Test pagination normalization with default values."""
        result = normalize_pagination(0, 50)
        assert result == {"skip": 0, "limit": 50}

    @pytest.mark.parametrize(
        "skip,limit,expected_skip,expected_limit",
        [
            (0, 10, 0, 10),
            (5, 25, 5, 25),
            (-1, 50, 0, 50),
            (10, -1, 10, 1),
            (20, 200, 20, 200),
            (-5, -10, 0, 1),
        ],
    )
    def test_normalize_pagination_parametrized(self, skip, limit, expected_skip, expected_limit):
        """Test pagination normalization with various parameter combinations."""
        result = normalize_pagination(skip, limit)
        assert result["skip"] == expected_skip
        assert result["limit"] == expected_limit
