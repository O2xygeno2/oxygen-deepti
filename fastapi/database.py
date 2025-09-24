import os
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from google.cloud.sql.connector import Connector

class Base(DeclarativeBase):
    pass

# Initialize Cloud SQL Connector
connector = Connector()

async def get_connection():
    """Get database connection using Cloud SQL Connector"""
    connection = await connector.connect_async(
        "master-shell-468709-v8:asia-south1:fastapi-db",  # Your instance connection name
        "asyncpg",
        user=os.getenv("DB_USER", "fastapi-db-user"),
        password=os.getenv("DB_PASSWORD", "fastapiDB@12"),
        db=os.getenv("DB_NAME", "fastapi-db-name")
    )
    return connection

# Create async engine with Cloud SQL Connector
engine = create_async_engine(
    "postgresql+asyncpg://",
    async_creator=get_connection,
    echo=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def test_connection():
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
