# FastAPI Template

[![Tests](https://github.com/Toches15/fastapi-template/actions/workflows/test.yml/badge.svg)](https://github.com/Toches15/fastapi-template/actions/workflows/test.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A robust, production-ready FastAPI template with best practices, dependency injection, and comprehensive tooling.

## Features

- **🏗️ Clean Architecture**: Dependency injection, separation of concerns, SOLID principles
- **⚙️ Configuration Management**: Environment-based settings with pydantic-settings validation
- **📝 Structured Logging**: Centralized logging with request tracking and proper formatting
- **🛡️ Error Handling**: Comprehensive exception handling with consistent JSON responses
- **🔍 Request Tracking**: Middleware for unique request IDs and performance timing
- **📚 API Documentation**: Auto-generated Swagger/OpenAPI docs with proper organization
- **🧪 Testing Ready**: Pytest setup with fixtures and example tests
- **🐳 Docker Support**: Production-ready containerization with multi-stage builds
- **🛠️ Development Tools**: Makefile, linting (Ruff), type checking (MyPy), formatting
- **🔌 Database Ready**: Multi-backend database setup with automatic lifecycle management (PostgreSQL, MySQL, SQLite, MongoDB)
- **🔐 Security Utilities**: Cryptographic functions and authentication patterns
- **📊 Health Monitoring**: Built-in health checks for load balancers and monitoring

## Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI application entry point
├── dependencies.py      # Dependency injection container
├── config/              # Configuration management
│   ├── __init__.py
│   └── cfg.py          # Settings and configuration
├── models/              # Pydantic models for API documentation
│   ├── __init__.py
│   └── responses.py    # Response models for Swagger docs
├── api/                 # API routes organization
│   └── v1/
│       ├── __init__.py
│       └── router.py    # API v1 routes with dependency examples
├── core/                # Core application modules
│   ├── __init__.py
│   ├── database.py     # Database configuration (multi-backend)
│   ├── exceptions.py   # Custom exceptions and handlers
│   ├── logging.py      # Logging configuration
│   └── middleware.py   # Custom middleware
├── services/            # Business logic services
│   ├── __init__.py
│   └── base.py         # Base service classes and interfaces
└── utils/               # Utility functions
    ├── __init__.py
    ├── helpers.py      # General helper functions
    └── security.py     # Security utilities

tests/                   # Test suite
├── __init__.py
├── conftest.py         # Pytest configuration and fixtures
└── test_main.py        # Main application tests

# Additional files
├── Dockerfile          # Docker configuration
├── .dockerignore       # Docker ignore file
├── Makefile           # Common development tasks
├── .env.example       # Environment variables template
└── pyproject.toml     # Project configuration with dev dependencies
```

## Configuration

Copy `.env.example` to `.env` and configure your environment variables:

```bash
cp .env.example .env
```

Key configuration options:
- `ENVIRONMENT`: development, staging, or production
- `DEBUG`: Enable/disable debug mode
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `SECRET_KEY`: Cryptographic secret (must be changed in production)
- `USE_DATABASE`: Enable database support (defaults to SQLite if no URL provided)
- `DATABASE_URL`: Database connection URL (optional, uses SQLite if not set)

## Quick Start

### 1. Install Dependencies
```bash
# Using uv (recommended)
uv sync

# Install with development dependencies
uv sync --extra dev

# Or using pip
pip install -e .
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Or use development environment
cp .env.dev .env

# Load environment variables (optional)
make env      # Load from .env
make env-dev  # Load from .env.dev
```

### 3. Run the Application
```bash
# Development (with auto-reload)
make run
# or
uv run python main.py

# Production
make run-prod
# or
ENVIRONMENT=production uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Development Commands
```bash
make help          # Show all available commands
make env           # Load environment variables from .env
make env-dev       # Load environment variables from .env.dev
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting and type checking
make format        # Format code with ruff
make clean         # Clean up cache files
make requirements  # Export production dependencies to requirements.txt
```

## API Documentation

When running in development mode, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### System Endpoints
- **`GET /`** - API information, version, and documentation links
- **`GET /system/health`** - Health check with database status for monitoring and load balancers

### Example API Endpoints (v1)
- **`GET /api/v1/example`** - Example endpoint with dependency injection
- **`GET /api/v1/protected`** - Protected endpoint requiring authentication
- **`GET /api/v1/items`** - Paginated items list with sorting
- **`POST /api/v1/upload`** - File upload with validation

### Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Customization Guide

### 1. Adding New Routes
```python
# Step 1: Create route module (e.g., app/api/v1/users.py)
from fastapi import APIRouter
from app.dependencies import SettingsDep, AuthenticatedUserDep

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def list_users(settings: SettingsDep):
    return {"users": []}

@router.get("/me")
async def get_current_user(user: AuthenticatedUserDep):
    return {"user": user}

# Step 2: Register in app/api/v1/router.py
from app.api.v1 import users
api_router.include_router(users.router)

# That's it! Routes are automatically available at /api/v1/users/
```

### 2. Database Integration

#### Quick Setup (SQLite - Development)
```bash
# In your .env file
USE_DATABASE=true
# No DATABASE_URL needed - automatically uses SQLite
```

#### Production Database
```bash
# In your .env file  
USE_DATABASE=true
DATABASE_URL=postgresql://user:password@localhost/dbname
```

#### Usage in Routes
```python
from sqlmodel import select
from app.models.user import User  # Your SQLModel models

@router.get("/users")
async def get_users(db: DatabaseSessionDep):
    # SQLModel session automatically injected
    statement = select(User)
    result = await db.execute(statement)
    users = result.scalars().all()
    return {"users": users}

# Raw SQL if needed
@router.get("/users/raw")
async def get_users_raw(db: DatabaseSessionDep):
    from sqlmodel import text
    result = await db.execute(text("SELECT * FROM users"))
    return {"users": result.fetchall()}

# Or for databases library/MongoDB:
@router.get("/items") 
async def get_items(db: DatabaseDep):
    # Database instance automatically injected
    return await db.fetch_all("SELECT * FROM items")
```

#### Supported Databases
- **SQLite**: `sqlite:///./app.db` (default when `USE_DATABASE=true`)
- **PostgreSQL**: `postgresql://user:pass@host/db`
- **MySQL**: `mysql://user:pass@host/db`  
- **MongoDB**: `mongodb://host:port/db`

### 3. Authentication
```python
# Uncomment JWT utilities in app/utils/security.py
# Update get_current_user in app/dependencies.py
# Use AuthenticatedUserDep in protected routes
```

### 4. Configuration
```python
# Add settings to app/config/cfg.py
class Settings(BaseSettings):
    your_api_key: str | None = Field(default=None)
    
# Add to .env
YOUR_API_KEY=your-key-here
```

### 5. Business Services
Services are automatically managed with lifecycle support. See `app/services/README.md` for detailed examples.

```python
# Create stateless service (no initialization needed)
class LLMService(BaseService):
    async def generate_text(self, prompt: str) -> str:
        # Business logic here
        return result

# Create stateful service (needs initialization)  
class RedisService(StatefulService):
    async def initialize(self):
        self.client = redis.from_url(self.settings.redis_url)
    
    async def cleanup(self):
        await self.client.close()

# Register in ServiceContainer and use in routes
@router.post("/generate")
async def generate_text(services: ServicesDep):
    return await services.llm_service.generate_text(prompt)
```

### 6. Utilities
```python
# Add project-specific functions to app/utils/
# Import and use throughout your application
```

## Docker Deployment

### Build and Run
```bash
# Build image
make docker-build

# Run container
make docker-run

# Or manually
docker build -t fastapi-template .
docker run -p 8000:8000 fastapi-template
```

### Production Deployment
```bash
# With environment variables
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=your-db-url \
  fastapi-template
```

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/test_main.py -v
```

## Dependency Management

This template uses **uv** for fast, reliable dependency management:

### Export Dependencies
```bash
# Export production dependencies to requirements.txt
uv export --format requirements-txt --no-hashes --no-dev -o requirements.txt

# Or use the Makefile shortcut
make requirements
```

### Managing Dependencies
```bash
# Add a new dependency
uv add fastapi-users

# Add a development dependency
uv add --dev pytest-cov

# Update all dependencies
uv sync --upgrade
```

## Code Quality

This template includes comprehensive code quality tools:

- **Ruff**: Fast Python linter and formatter
- **MyPy**: Static type checking
- **Pytest**: Testing framework with async support
- **Pre-configured**: Line length set to 120, E501 ignored

```bash
make lint    # Check code quality
make format  # Auto-format code
```
## Architecture Highlights

### Dependency Injection

The `app/dependencies.py` file provides a centralized way to manage dependencies and avoid circular imports:

### Available Dependencies

```python
from app.dependencies import (
    SettingsDep,           # Application settings
    ServicesDep,           # Service container
    CurrentUserDep,        # Optional current user
    AuthenticatedUserDep,  # Required authenticated user
    CommonQueryDep,        # Pagination and sorting
    DatabaseSessionDep,    # Database session (SQLAlchemy)
    DatabaseDep,           # Database instance (databases/MongoDB)
)

@router.get("/example")
async def example_endpoint(
    settings: SettingsDep,
    user: CurrentUserDep,
) -> dict:
    return {
        "environment": settings.environment,
        "user_authenticated": user is not None,
    }
```

### Service Container Pattern

The `ServiceContainer` class provides lazy-loaded services:

```python
# In dependencies.py
class ServiceContainer:
    @property
    def email_service(self):
        # Lazy initialization
        if self._email_service is None:
            self._email_service = EmailService(self.settings)
        return self._email_service
```

### Key Benefits

- **🔄 Avoid Circular Imports**: Centralized dependency management
- **🔒 Type Safety**: Full type hints and IDE support  
- **🧪 Testability**: Easy to mock dependencies in tests
- **📏 Consistency**: Standardized patterns across the application
- **⚡ Performance**: Cached instances with `@lru_cache()`
- **🏗️ SOLID Principles**: Dependency inversion, single responsibility
- **📦 Modular Design**: Clean separation of concerns
- **🔧 Production Ready**: Comprehensive error handling and monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting: `make test lint`
5. Submit a pull request

## License

This template is open source and available under the [MIT License](LICENSE).

---

**Ready to build something amazing?** 🚀

This template provides everything you need to start a production-ready FastAPI project. Simply clone, customize, and deploy!