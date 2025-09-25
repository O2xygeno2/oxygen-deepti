import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from google.cloud.sql.connector import Connector  # Correct import

# SQLAlchemy Base
class Base(DeclarativeBase):
    pass

# Cloud SQL Connector instance
connector = Connector()

# Fetch environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")  # optional, only if using IP directly
DB_PORT = os.getenv("DB_PORT", "5432")
CLOUD_SQL_CONNECTION_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME")

# Async connection function using Cloud SQL Connector
async def get_connection():
    print("🔍 Debug: DB connection variables")
    print(f"  DB_USER: {DB_USER}")
    print(f"  DB_PASSWORD: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'NOT SET'}")
    print(f"  DB_NAME: {DB_NAME}")
    print(f"  CLOUD_SQL_CONNECTION_NAME: {CLOUD_SQL_CONNECTION_NAME}")

    try:
        conn = await connector.connect_async(
            CLOUD_SQL_CONNECTION_NAME,
            driver="asyncpg",
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            # Optional: specify IP for local dev
            host=DB_HOST,
            port=int(DB_PORT)
        )
        print("✅ Successfully created async connection")
        return conn
    except Exception as e:
        print(f"❌ Failed to create DB connection: {e}")
        raise

# Create SQLAlchemy async engine
engine = create_async_engine(
    "postgresql+asyncpg://",
    async_creator=get_connection,
    echo=True,
    pool_pre_ping=True
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI
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
            print("🔍 Testing DB connection with SELECT 1")
            await conn.execute("SELECT 1")
        print("✅ DB test query succeeded")
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

# Create tables
async def create_tables():
    try:
        async with engine.begin() as conn:
            print("🔍 Running Base.metadata.create_all")
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")

