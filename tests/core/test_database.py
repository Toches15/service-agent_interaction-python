"""
Tests for database configuration and management.
"""

from unittest.mock import patch
import pytest

from app.core.database import DatabaseRegistry, SQLModelManager, configure_databases


class TestDatabaseRegistry:
    """Test database registry functionality."""

    def test_registry_initialization(self):
        """Test that registry initializes with empty databases."""
        registry = DatabaseRegistry()
        assert not registry.databases

    def test_register_sqlmodel_database(self):
        """Test registering a SQLModel database."""
        registry = DatabaseRegistry()
        registry.register_sqlmodel("test_db", "sqlite+aiosqlite:///test.db")

        assert "test_db" in registry.databases
        assert isinstance(registry.databases["test_db"], SQLModelManager)

    def test_get_database_existing(self):
        """Test getting an existing database."""
        registry = DatabaseRegistry()
        registry.register_sqlmodel("test_db", "sqlite+aiosqlite:///test.db")

        db = registry.get_database("test_db")
        assert isinstance(db, SQLModelManager)

    def test_get_database_nonexistent(self):
        """Test getting a non-existent database raises error."""
        registry = DatabaseRegistry()

        with pytest.raises(ValueError, match="Database 'nonexistent' not registered"):
            registry.get_database("nonexistent")

    @pytest.mark.asyncio
    async def test_connect_all_no_databases(self):
        """Test connect_all with no databases configured."""
        registry = DatabaseRegistry()

        # Should not raise any errors
        await registry.connect_all()

    @pytest.mark.asyncio
    async def test_health_check_all_empty(self):
        """Test health check with no databases."""
        registry = DatabaseRegistry()

        health = await registry.health_check_all()
        assert health == {}


class TestSQLModelManager:
    """Test SQLModel database manager."""

    def test_sqlmodel_manager_initialization(self):
        """Test SQLModel manager initialization."""
        manager = SQLModelManager("test", "sqlite+aiosqlite:///test.db")

        assert manager.name == "test"
        assert manager.connection_url == "sqlite+aiosqlite:///test.db"
        assert manager.is_connected is False
        assert manager.engine is None
        assert manager.session_factory is None


class TestDatabaseConfiguration:
    """Test database configuration function."""

    @patch("app.core.database.get_settings")
    @patch("app.core.database.db_registry")
    def test_configure_databases_disabled(self, mock_registry, mock_settings):
        """Test database configuration when disabled."""
        mock_settings.return_value.use_database = False

        configure_databases()

        # Should not register any databases
        mock_registry.register_sqlmodel.assert_not_called()

    # Note: These tests would require more complex mocking due to @lru_cache
    # For now, we test the components individually
    def test_configure_databases_function_exists(self):
        """Test that configure_databases function exists and is callable."""
        assert callable(configure_databases)
