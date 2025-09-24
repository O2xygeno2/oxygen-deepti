import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

class Base(DeclarativeBase):
    pass

# Your Cloud SQL instance configuration
DB_CONFIG = {
    "user": os.getenv("DB_USER", "postgres"),  # You'll need to set this
    "password": os.getenv("DB_PASSWORD", ""),  # Set via Secret Manager
    "host": os.getenv("DB_HOST", "10.231.0.3"),  # Private IP for better performance
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "postgres"),  # Your database name
    "connection_name": "master-shell-468709-v8:asia-south1:fastapi-db"
}

def get_database_url():
    """Get appropriate database URL based on environment"""
    
    # For Cloud Run (use private IP)
    if os.getenv("K_SERVICE"):  # Cloud Run environment
        return f"postgresql+asyncpg://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    
    # For local development (use public IP with SSL)
    return f"postgresql+asyncpg://{DB_CONFIG['user']}:{DB_CONFIG['password']}@34.100.220.171:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

DATABASE_URL = get_database_url()

# Create async engine optimized for your Cloud SQL instance
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "False").lower() == "true",
    future=True,
    poolclass=NullPool,  # Important for Cloud Run
    connect_args={
        "ssl": os.getenv("DB_SSL", "prefer"),  # SSL for public connections
        "server_settings": {
            "jit": "off",
            "statement_timeout": "30000",
            "lock_timeout": "10000"
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
