import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Fetch environment variables
DB_USER = os.getenv("DB_USER", "fastapi-db-user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "fastapiDB@12")
DB_NAME = os.getenv("DB_NAME", "fastapi-db-name")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")  # use Cloud SQL public IP or VPC hostname
DB_PORT = os.getenv("DB_PORT", "5432")

# Debug: print DB variables
print("🔍 Debug: DB connection variables")
print(f"  DB_USER: {DB_USER}")
print(f"  DB_PASSWORD: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'NOT SET'}")
print(f"  DB_NAME: {DB_NAME}")
print(f"  DB_HOST: {DB_HOST}")
print(f"  DB_PORT: {DB_PORT}")

# Create async SQLAlchemy engine
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Test DB connection
async def test_connection():
    try:
        async with engine.begin() as conn:
            print("🔍 Debug: Testing DB connection with SELECT 1")
            await conn.execute("SELECT 1")
        print("✅ Debug: DB test query succeeded")
        return True
    except Exception as e:
        print(f"❌ Debug: Database connection error: {e}")
        return False

# Create tables using SQLAlchemy Base metadata
async def create_tables():
    try:
        async with engine.begin() as conn:
            print("🔍 Debug: Running create_all on Base metadata")
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Debug: Tables created successfully")
    except Exception as e:
        print(f"❌ Debug: Failed to create tables: {e}")

# Optional: run quick test if executed directly
if __name__ == "__main__":
    asyncio.run(test_connection())
