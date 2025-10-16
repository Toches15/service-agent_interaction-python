# Service Creation Guide

This guide explains how to create and integrate services in our FastAPI template.

## Service Types & Patterns

### 1. Stateless Services (No Initialization)
**Use for:** Business logic, simple API wrappers, calculations

```python
# app/services/llm.py
from app.services.base import BaseService
import httpx

class LLMService(BaseService):
    """OpenAI/LLM service for text generation."""
    
    async def generate_text(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """Generate text using OpenAI API."""
        if not self.settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            return response.json()["choices"][0]["message"]["content"]
```

### 2. Stateful Services (Need Initialization)
**Use for:** Database connections, cache services, message queues

```python
# app/services/cache.py
from app.services.base import StatefulService, CacheServiceInterface
import redis.asyncio as redis

class RedisService(StatefulService, CacheServiceInterface):
    """Redis cache service with persistent connection."""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.redis_client = None
    
    async def initialize(self):
        """Initialize Redis connection."""
        if not self.settings.redis_url:
            raise ValueError("Redis URL not configured")
        
        self.redis_client = redis.from_url(self.settings.redis_url)
        await self.redis_client.ping()  # Test connection
        self.logger.info("Redis connection established")
    
    async def cleanup(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.logger.info("Redis connection closed")
    
    async def health_check(self) -> bool:
        """Check Redis health."""
        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False
    
    async def get(self, key: str):
        return await self.redis_client.get(key)
    
    async def set(self, key: str, value, ttl: int = 300):
        await self.redis_client.setex(key, ttl, value)
    
    async def delete(self, key: str):
        await self.redis_client.delete(key)
```

### 3. Database Services (Uses Existing DB Connections)
**Use for:** Business logic that needs database access using connections from `core/database.py`

```python
# app/services/user.py
from app.services.base import BaseService
from app.core.database import db_registry
from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User, UserCreate, UserRead
from sqlmodel import select, text
from typing import List, Optional

class UserService(BaseService):
    """User business logic using existing database connections."""
    
    async def get_user_by_id(self, user_id: int) -> UserRead:
        """Get user by ID with business validation."""
        if user_id <= 0:
            raise ValidationError("User ID must be positive")
        
        # Use existing database connection from core/database.py
        db_manager = db_registry.get_database("main")
        
        # For SQLModel databases
        if hasattr(db_manager, 'get_session'):
            async for session in db_manager.get_session():
                # Type-safe SQLModel query
                statement = select(User).where(User.id == user_id)
                result = await session.execute(statement)
                user = result.scalar_one_or_none()
                
                if not user:
                    raise NotFoundError(f"User {user_id} not found")
                
                # Return as Pydantic model for API serialization
                return UserRead.model_validate(user)
    
    async def create_user(self, user_data: UserCreate) -> UserRead:
        """Create new user with business validation."""
        # Business validation
        if not user_data.email:
            raise ValidationError("Email is required")
        
        # Use existing database connection
        db_manager = db_registry.get_database("main")
        
        async for session in db_manager.get_session():
            # Check if email already exists (type-safe)
            statement = select(User).where(User.email == user_data.email)
            existing = await session.execute(statement)
            
            if existing.scalar_one_or_none():
                raise ValidationError("Email already exists")
            
            # Create new user
            db_user = User.model_validate(user_data.model_dump(exclude={"password"}))
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            
            return UserRead.model_validate(db_user)
        
        # For databases library or MongoDB
        else:
            database = db_manager.database
            query = "SELECT * FROM users WHERE id = :user_id AND deleted_at IS NULL"
            user_row = await database.fetch_one(query, {"user_id": user_id})
            
            if not user_row:
                raise NotFoundError(f"User {user_id} not found")
            
            return dict(user_row)
    
    async def create_user(self, user_data: Dict) -> Dict:
        """Create new user with business validation."""
        # Business validation
        if not user_data.get("email"):
            raise ValidationError("Email is required")
        
        # Use existing database connection
        db_manager = db_registry.get_database("main")
        
        async for session in db_manager.get_session():
            # Check if email already exists
            existing = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": user_data["email"]}
            )
            
            if existing.fetchone():
                raise ValidationError("Email already exists")
            
            # Insert new user
            result = await session.execute(
                text("""
                    INSERT INTO users (username, email, created_at) 
                    VALUES (:username, :email, NOW()) 
                    RETURNING id, username, email, created_at
                """),
                {
                    "username": user_data["username"],
                    "email": user_data["email"]
                }
            )
            
            new_user = result.fetchone()
            return dict(new_user._mapping)
    
    def _get_display_name(self, user_data: Dict) -> str:
        """Business logic for display name."""
        if user_data.get("full_name"):
            return user_data["full_name"]
        elif user_data.get("username"):
            return f"@{user_data['username']}"
        else:
            return f"User #{user_data['id']}"
    
    async def _get_user_permissions(self, session, user_id: int) -> List[str]:
        """Get user permissions - complex business logic."""
        result = await session.execute(
            text("""
                SELECT DISTINCT p.name 
                FROM permissions p
                JOIN role_permissions rp ON p.id = rp.permission_id
                JOIN user_roles ur ON rp.role_id = ur.role_id
                WHERE ur.user_id = :user_id
            """),
            {"user_id": user_id}
        )
        
        return [row[0] for row in result.fetchall()]
```

### 4. Pure Business Logic (No Database)
**Use for:** Calculations, transformations, pure functions

```python
# app/services/business.py
from app.services.base import BaseService
from typing import Dict, List

class OrderService(BaseService):
    """Business logic for order processing."""
    
    def calculate_total(self, items: List[Dict]) -> float:
        """Calculate order total with tax."""
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        tax = subtotal * 0.08  # 8% tax
        return subtotal + tax
    
    async def process_order(self, order_data: Dict) -> Dict:
        """Process an order (business logic only)."""
        total = self.calculate_total(order_data["items"])
        
        return {
            "order_id": f"ORD-{hash(str(order_data))}",
            "total": total,
            "status": "processed"
        }
```

## Integration Steps

### Step 1: Create the Service
Create your service file in `app/services/` following the patterns above.

### Step 2: Register in ServiceContainer
Add a property to the ServiceContainer in `app/dependencies.py`:

```python
# In ServiceContainer class
@property
def llm_service(self) -> LLMService:
    """Get LLM service instance."""
    if 'llm' not in self._services:
        from app.services.llm import LLMService
        self._services['llm'] = LLMService(self.settings)
    return self._services['llm']

@property
def cache_service(self) -> RedisService:
    """Get cache service instance."""
    if 'cache' not in self._services:
        from app.services.cache import RedisService
        self._services['cache'] = RedisService(self.settings)
    return self._services['cache']

@property
def user_service(self) -> UserService:
    """Get user service instance."""
    if 'user' not in self._services:
        from app.services.user import UserService
        self._services['user'] = UserService(self.settings)
    return self._services['user']

@property
def order_service(self) -> OrderService:
    """Get order service instance."""
    if 'order' not in self._services:
        from app.services.business import OrderService
        self._services['order'] = OrderService(self.settings)
    return self._services['order']
```

### Step 3: Use in Routes
Inject the service container and use your service:

```python
# In your route files
from app.dependencies import ServicesDep

@router.post("/generate")
async def generate_text(
    prompt: str,
    services: ServicesDep
):
    result = await services.llm_service.generate_text(prompt)
    return {"generated_text": result}

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    services: ServicesDep
):
    # Use database service (uses existing DB connection)
    user = await services.user_service.get_user_by_id(user_id)
    return user

@router.post("/users")
async def create_user(
    user_data: dict,
    services: ServicesDep
):
    # Business logic with database access
    new_user = await services.user_service.create_user(user_data)
    return new_user

@router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    services: ServicesDep
):
    # Use cache service
    cached = await services.cache_service.get(f"order:{order_id}")
    if cached:
        return cached
    
    # Process with business logic
    order = await services.order_service.process_order(order_data)
    
    # Cache result
    await services.cache_service.set(f"order:{order_id}", order)
    return order
```

### Step 4: Add Configuration (if needed)
Add any required settings to `app/config/cfg.py`:

```python
# In Settings class
openai_api_key: str | None = Field(default=None, description="OpenAI API key")
redis_url: str | None = Field(default=None, description="Redis connection URL")
```

And to `.env.example`:
```bash
OPENAI_API_KEY=your-openai-key
REDIS_URL=redis://localhost:6379/0
```

## Database Access Patterns

### Using Existing Database Connections
Services can access databases configured in `core/database.py` without managing connections:

```python
# Get the database manager (connection already established)
db_manager = db_registry.get_database("main")  # or "analytics", "read_replica", etc.

# For SQLAlchemy databases (PostgreSQL, MySQL, SQLite)
async for session in db_manager.get_session():
    result = await session.execute(text("SELECT * FROM users"))
    # Session automatically commits/rollbacks and closes

# For databases library or MongoDB
database = db_manager.database
result = await database.fetch_all("SELECT * FROM users")
```

### Key Points:
- **No connection management**: Database connections are handled by `core/database.py`
- **Use BaseService**: Database services don't need StatefulService (no initialization)
- **Multiple databases**: Access different databases by name (`"main"`, `"analytics"`, etc.)
- **Automatic cleanup**: Sessions and transactions are handled automatically

## Service Lifecycle

### Automatic Management
- **BaseService (Stateless)**: No lifecycle methods - services work immediately
- **Database Services**: Use BaseService + existing DB connections (no initialization needed)
- **StatefulService (Stateful)**: Automatically initialized during app startup and cleaned up during shutdown
- **Health checks**: StatefulService health checks included in `/system/health` endpoint automatically

### Manual Management
If you need custom lifecycle control, use StatefulService:

```python
# In your service
class CustomService(StatefulService):
    async def initialize(self):
        # Custom initialization logic (REQUIRED for StatefulService)
        self.logger.info("Custom service starting...")
    
    async def cleanup(self):
        # Custom cleanup logic (REQUIRED for StatefulService)
        self.logger.info("Custom service stopping...")
    
    async def health_check(self) -> bool:
        # Health check logic (REQUIRED for StatefulService)
        return True
```

## Best Practices

1. **Choose the right base class**:
   - **BaseService**: For stateless services, business logic, database services using existing connections
   - **StatefulService**: Only for services that need their own connection management (Redis, external APIs)

2. **Database access**:
   - **Use existing connections**: Access databases through `db_registry.get_database()`
   - **No connection management**: Let `core/database.py` handle all database lifecycle
   - **Multiple databases**: Use different database names for different purposes

3. **Service design**:
   - **Implement interfaces**: Create interfaces for complex services
   - **Lazy loading**: Services are created only when first accessed
   - **Error handling**: Services handle their own errors gracefully
   - **Configuration**: Use settings for all configuration values
   - **Logging**: Use self.logger for consistent logging

4. **Health checks**: StatefulService requires health_check() implementation

## Examples by Use Case

- **User Service**: BaseService + existing database connection (PostgreSQL/MySQL)
- **LLM Service**: BaseService, stateless, uses API keys, no initialization
- **Cache Service**: StatefulService, manages Redis connection, requires initialization
- **Email Service**: Could be BaseService (SMTP per request) or StatefulService (connection pool)
- **File Storage**: BaseService for cloud storage, StatefulService for local connections
- **Business Logic**: BaseService, pure functions, no external dependencies

## Architecture Summary

```
Core Infrastructure (app/core/database.py)
├── PostgreSQL (main)           ← Managed by database.py
├── Analytics DB                ← Managed by database.py  
└── Read Replicas              ← Managed by database.py

Business Services (app/services/)
├── UserService(BaseService)    ← Uses existing DB connections
├── OrderService(BaseService)   ← Pure business logic
├── RedisService(StatefulService) ← Manages own connection
└── LLMService(BaseService)     ← Stateless API calls
```

This pattern gives you maximum flexibility while maintaining consistency and proper lifecycle management!

This pattern gives you maximum flexibility while maintaining consistency and proper lifecycle management!