"""
Tests for security utility functions.
"""

import pytest

from app.utils.security import generate_random_string, hash_string


class TestSecurity:
    """Test security utility functions."""

    def test_generate_random_string_default_length(self):
        """Test random string generation with default length."""
        result = generate_random_string()
        # Note: token_urlsafe returns base64-encoded string, so length varies
        assert len(result) > 0
        assert isinstance(result, str)

    def test_generate_random_string_custom_length(self):
        """Test random string generation with custom length."""
        length = 16
        result = generate_random_string(length)
        # Length will be approximately length * 4/3 due to base64 encoding
        assert len(result) > 0
        assert isinstance(result, str)

    def test_generate_random_string_uniqueness(self):
        """Test that generated strings are unique."""
        string1 = generate_random_string()
        string2 = generate_random_string()
        assert string1 != string2

    def test_generate_random_string_zero_length(self):
        """Test random string generation with zero length."""
        result = generate_random_string(0)
        assert result == ""

    def test_hash_string_returns_string(self):
        """Test that string hashing returns a string."""
        test_string = "test_string_123"
        hashed = hash_string(test_string)
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA-256 hex digest is 64 characters

    def test_hash_string_consistent(self):
        """Test that hashing the same string gives consistent results."""
        test_string = "test_string_123"
        hash1 = hash_string(test_string)
        hash2 = hash_string(test_string)
        assert hash1 == hash2

    def test_hash_string_different_inputs(self):
        """Test that different strings produce different hashes."""
        string1 = "test_string_1"
        string2 = "test_string_2"
        hash1 = hash_string(string1)
        hash2 = hash_string(string2)
        assert hash1 != hash2

    def test_hash_string_empty_string(self):
        """Test hashing an empty string."""
        result = hash_string("")
        assert isinstance(result, str)
        assert len(result) == 64

    @pytest.mark.parametrize(
        "test_input",
        [
            "simple",
            "complex_string_123!@#",
            "unicode_string_🔒",
            "very_long_string_" + "x" * 100,
            "",
            "123",
            "special chars: !@#$%^&*()",
        ],
    )
    def test_hash_string_various_inputs(self, test_input):
        """Test string hashing with various inputs."""
        result = hash_string(test_input)
        assert isinstance(result, str)
        assert len(result) == 64

        # Test consistency
        assert hash_string(test_input) == result
