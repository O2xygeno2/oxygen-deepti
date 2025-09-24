import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

class Base(DeclarativeBase):
    pass

def get_database_url():
    """Get appropriate database URL based on environment"""
    
    # Get credentials from environment variables (never hardcode!)
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    
    if not all([db_user, db_password, db_name]):
        raise ValueError("Missing required database environment variables")
    
    # For Cloud Run - use private IP with Cloud SQL connector context
    if os.getenv("K_SERVICE"):  # Cloud Run environment
        # In Cloud Run, we should use the Cloud SQL Proxy or connector
        # For now, use private IP but this requires VPC connectivity
        db_host = os.getenv("DB_HOST", "10.231.0.3")
        return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:5432/{db_name}"
    
    # For local development - use public IP with SSL
    db_host = os.getenv("DB_HOST", "34.100.220.171")
    ssl_mode = "require"  # Force SSL for public connections
    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:5432/{db_name}?ssl={ssl_mode}"

try:
    DATABASE_URL = get_database_url()
except ValueError as e:
    print(f"Database configuration error: {e}")
    DATABASE_URL = None

if DATABASE_URL:
    # Create async engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=os.getenv("DB_ECHO", "False").lower() == "true",
        future=True,
        poolclass=NullPool,
        connect_args={}
    )

    # Async session maker
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )
else:
    engine = None
    AsyncSessionLocal = None

async def get_db():
    """Dependency for getting async database session"""
    if not AsyncSessionLocal:
        raise RuntimeError("Database not configured properly")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def test_connection():
    """Test database connection"""
    if not engine:
        return False
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

async def create_tables():
    """Create database tables"""
    if not engine:
        raise RuntimeError("Database engine not configured")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
