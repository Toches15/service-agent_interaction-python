"""
Database configuration and lifecycle management.

This module provides a flexible database setup that automatically handles
initialization and cleanup for configured databases during application lifecycle.
"""

import asyncio
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, AsyncGenerator

from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager(ABC):
    """Abstract base class for database managers."""

    def __init__(self, name: str, connection_url: str):
        self.name = name
        self.connection_url = connection_url
        self.is_connected = False

    @abstractmethod
    async def connect(self) -> None:
        """Initialize database connection."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if database is healthy."""


class SQLModelManager(DatabaseManager):
    """SQLModel database manager (built on SQLAlchemy)."""

    def __init__(self, name: str, connection_url: str, **kwargs):
        super().__init__(name, connection_url)
        self.engine = None
        self.session_factory = None
        self.engine_kwargs = kwargs

    async def connect(self) -> None:
        """Initialize SQLModel engine and session factory."""
        try:
            # Import here to avoid dependency issues if not installed
            from sqlmodel import text

            # SQLModel doesn't have async engine yet, so we use SQLAlchemy's for async
            # This is the recommended approach for FastAPI + SQLModel
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
            from sqlalchemy.orm import sessionmaker

            self.engine = create_async_engine(
                self.connection_url, echo=get_settings().debug, future=True, **self.engine_kwargs
            )

            self.session_factory = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            self.is_connected = True
            logger.info(f"SQLModel database '{self.name}' connected successfully")

        except ImportError as e:
            logger.warning(f"SQLModel/SQLAlchemy import failed for database '{self.name}': {e}")
        except Exception as e:
            logger.error(f"Failed to connect to SQLModel database '{self.name}': {e}")
            raise

    async def disconnect(self) -> None:
        """Close SQLModel engine."""
        if self.engine and self.is_connected:
            try:
                await self.engine.dispose()
                self.is_connected = False
                logger.info(f"SQLModel database '{self.name}' disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting SQLModel database '{self.name}': {e}")

    async def health_check(self) -> bool:
        """Check SQLModel database health."""
        if not self.is_connected or not self.engine:
            return False
        try:
            from sqlmodel import text

            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def get_session(self) -> AsyncGenerator[Any, None]:
        """Get database session."""
        if not self.session_factory:
            raise RuntimeError(f"Database '{self.name}' not connected")

        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


class DatabasesManager(DatabaseManager):
    """Databases library manager."""

    def __init__(self, name: str, connection_url: str, **kwargs):
        super().__init__(name, connection_url)
        self.database = None
        self.database_kwargs = kwargs

    async def connect(self) -> None:
        """Initialize databases connection."""
        try:
            # Import here to avoid dependency issues if not installed
            import databases

            self.database = databases.Database(self.connection_url, **self.database_kwargs)
            await self.database.connect()

            self.is_connected = True
            logger.info(f"Databases library database '{self.name}' connected successfully")

        except ImportError:
            logger.warning(f"Databases library not installed, skipping database '{self.name}'")
        except Exception as e:
            logger.error(f"Failed to connect to database '{self.name}': {e}")
            raise

    async def disconnect(self) -> None:
        """Close databases connection."""
        if self.database and self.is_connected:
            try:
                await self.database.disconnect()
                self.is_connected = False
                logger.info(f"Databases library database '{self.name}' disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting database '{self.name}': {e}")

    async def health_check(self) -> bool:
        """Check database health."""
        if not self.is_connected or not self.database:
            return False
        try:
            await self.database.fetch_one("SELECT 1")
            return True
        except Exception:
            return False


class MongoManager(DatabaseManager):
    """MongoDB manager."""

    def __init__(self, name: str, connection_url: str, database_name: str = "main", **kwargs):
        super().__init__(name, connection_url)
        self.client = None
        self.database = None
        self.database_name = database_name
        self.client_kwargs = kwargs

    async def connect(self) -> None:
        """Initialize MongoDB connection."""
        try:
            # Import here to avoid dependency issues if not installed
            from motor.motor_asyncio import AsyncIOMotorClient

            self.client = AsyncIOMotorClient(self.connection_url, **self.client_kwargs)
            self.database = self.client[self.database_name]

            # Test connection
            await self.client.admin.command("ping")

            self.is_connected = True
            logger.info(f"MongoDB database '{self.name}' connected successfully")

        except ImportError:
            logger.warning(f"Motor (MongoDB) not installed, skipping database '{self.name}'")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB '{self.name}': {e}")
            raise

    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client and self.is_connected:
            try:
                self.client.close()
                self.is_connected = False
                logger.info(f"MongoDB database '{self.name}' disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting MongoDB '{self.name}': {e}")

    async def health_check(self) -> bool:
        """Check MongoDB health."""
        if not self.is_connected or not self.client:
            return False
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False


class DatabaseRegistry:
    """Registry for managing multiple database connections."""

    def __init__(self):
        self.databases: dict[str, DatabaseManager] = {}

    def register_sqlmodel(self, name: str, connection_url: str, **kwargs) -> None:
        """Register a SQLModel database."""
        self.databases[name] = SQLModelManager(name, connection_url, **kwargs)

    # Alias for backward compatibility
    def register_sqlalchemy(self, name: str, connection_url: str, **kwargs) -> None:
        """Register a SQLModel database (alias for backward compatibility)."""
        self.register_sqlmodel(name, connection_url, **kwargs)

    def register_databases(self, name: str, connection_url: str, **kwargs) -> None:
        """Register a databases library database."""
        self.databases[name] = DatabasesManager(name, connection_url, **kwargs)

    def register_mongo(self, name: str, connection_url: str, database_name: str = "main", **kwargs) -> None:
        """Register a MongoDB database."""
        self.databases[name] = MongoManager(name, connection_url, database_name, **kwargs)

    async def connect_all(self) -> None:
        """Connect to all registered databases."""
        if not self.databases:
            logger.info("No databases configured, skipping database initialization")
            return

        logger.info(f"Initializing {len(self.databases)} database(s)...")

        # Connect to databases concurrently
        tasks = []
        for db_manager in self.databases.values():
            tasks.append(self._safe_connect(db_manager))

        await asyncio.gather(*tasks, return_exceptions=True)

        connected_count = sum(1 for db in self.databases.values() if db.is_connected)
        logger.info(f"Database initialization complete: {connected_count}/{len(self.databases)} connected")

    async def disconnect_all(self) -> None:
        """Disconnect from all databases."""
        if not self.databases:
            return

        logger.info("Shutting down database connections...")

        # Disconnect from databases concurrently
        tasks = []
        for db_manager in self.databases.values():
            if db_manager.is_connected:
                tasks.append(self._safe_disconnect(db_manager))

        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Database shutdown complete")

    async def health_check_all(self) -> dict[str, bool]:
        """Check health of all databases."""
        results = {}
        for name, db_manager in self.databases.items():
            try:
                results[name] = await db_manager.health_check()
            except Exception:
                results[name] = False
        return results

    def get_database(self, name: str) -> DatabaseManager:
        """Get a database manager by name."""
        if name not in self.databases:
            raise ValueError(f"Database '{name}' not registered")
        return self.databases[name]

    async def _safe_connect(self, db_manager: DatabaseManager) -> None:
        """Safely connect to a database with error handling."""
        try:
            await db_manager.connect()
        except Exception as e:
            logger.error(f"Failed to connect to database '{db_manager.name}': {e}")

    async def _safe_disconnect(self, db_manager: DatabaseManager) -> None:
        """Safely disconnect from a database with error handling."""
        try:
            await db_manager.disconnect()
        except Exception as e:
            logger.error(f"Failed to disconnect from database '{db_manager.name}': {e}")


# Global database registry
db_registry = DatabaseRegistry()


@lru_cache()
def configure_databases() -> None:
    """
    Configure databases based on settings.

    Add your database configurations here. Only configured databases
    will be initialized during application startup.

    Uses @lru_cache() to ensure configuration only happens once.
    """
    settings = get_settings()

    # Configure database if enabled
    if settings.use_database:
        if settings.database_url:
            # Use provided database URL
            db_url = str(settings.database_url)

            # Auto-detect database type from URL
            if db_url.startswith(("postgresql://", "postgresql+asyncpg://")):
                db_registry.register_sqlmodel("main", db_url)
            elif db_url.startswith(("sqlite", "sqlite+aiosqlite")):
                db_registry.register_sqlmodel("main", db_url)
            elif db_url.startswith("mysql"):
                db_registry.register_sqlmodel("main", db_url)
            elif db_url.startswith("mongodb://"):
                db_registry.register_mongo("main", db_url)
            else:
                # Default to databases library for other URLs
                db_registry.register_databases("main", db_url)
        else:
            # No URL provided, default to SQLite in temp directory
            import os

            os.makedirs("temp", exist_ok=True)
            sqlite_url = "sqlite+aiosqlite:///./temp/app.db"
            db_registry.register_sqlmodel("main", sqlite_url)
            logger.info("No DATABASE_URL provided, using default SQLModel database: ./temp/app.db")

    # Add more database configurations here:
    #
    # Example: Secondary PostgreSQL database for analytics
    # if hasattr(settings, 'analytics_db_url') and settings.analytics_db_url:
    #     db_registry.register_sqlalchemy("analytics", settings.analytics_db_url)
    #
    # Example: Read replica database
    # if hasattr(settings, 'read_replica_url') and settings.read_replica_url:
    #     db_registry.register_sqlalchemy("read_replica", settings.read_replica_url)


# Convenience functions for dependency injection
async def get_main_db_session():
    """Get main database session (for dependency injection)."""
    db_manager = db_registry.get_database("main")
    if isinstance(db_manager, SQLModelManager):
        async for session in db_manager.get_session():
            yield session
    else:
        raise ValueError("Main database is not a SQLModel database")


@lru_cache()
def get_main_database():
    """
    Get main database instance (for databases library or MongoDB).

    Uses @lru_cache() to return the same instance on repeated calls.
    """
    db_manager = db_registry.get_database("main")
    if isinstance(db_manager, DatabasesManager):
        return db_manager.database
    elif isinstance(db_manager, MongoManager):
        return db_manager.database
    else:
        raise ValueError("Main database is not a databases library or MongoDB database")
