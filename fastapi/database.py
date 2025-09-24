import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
import asyncpg

class Base(DeclarativeBase):
    pass

# Environment configuration
DB_CONFIG = {
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "postgres"),
    "ssl": os.getenv("DB_SSL", "prefer")
}

def create_async_engine_url():
    """Create appropriate async database URL based on environment"""
    
    # For Cloud Run with Cloud SQL private IP (recommended)
    if os.getenv("CLOUD_SQL_CONNECTION_NAME"):
        # Using private IP connection
        return f"postgresql+asyncpg://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    
    # For local development with public IP
    return f"postgresql+asyncpg://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Create async engine with optimization for Cloud Run
DATABASE_URL = create_async_engine_url()

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "False").lower() == "true",
    future=True,
    poolclass=NullPool,  # Important for Cloud Run - no connection pooling at app level
    connect_args={
        "server_settings": {
            "jit": "off",  # Improve performance for short-lived connections
            "statement_timeout": "30000",  # 30 second timeout
        }
    }
)

# Async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

async def get_db():
    """Dependency for getting async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def test_connection():
    """Test database connection"""
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

async def create_tables():
    """Create database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
