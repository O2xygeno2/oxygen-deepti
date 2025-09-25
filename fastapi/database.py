import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from google.cloud.sql.connector import Connector  # Correct import

class Base(DeclarativeBase):
    pass

# Initialize Cloud SQL Connector
connector = Connector()  # single Connector instance

async def get_connection():
    """Get database connection using Cloud SQL Python Connector"""

    db_user = os.getenv("DB_USER", "fastapi-db-user")
    db_password = os.getenv("DB_PASSWORD", "fastapiDB@12")
    db_name = os.getenv("DB_NAME", "fastapi-db-name")
    instance_conn_name = os.getenv("INSTANCE_CONNECTION_NAME", "master-shell-468709-v8:asia-south1:fastapi-db")

    print("🔍 Debug: DB connection variables")
    print(f"  DB_USER: {db_user}")
    print(f"  DB_PASSWORD: {'*' * len(db_password) if db_password else 'NOT SET'}")
    print(f"  DB_NAME: {db_name}")
    print(f"  INSTANCE_CONNECTION_NAME: {instance_conn_name}")

    try:
        conn = await connector.connect_async(
            instance_conn_name,
            driver="asyncpg",
            user=db_user,
            password=db_password,
            db=db_name
        )
        print("✅ Debug: Successfully created async connection object")
        return conn
    except Exception as e:
        print(f"❌ Debug: Failed to create DB connection: {e}")
        raise

# Create SQLAlchemy async engine using the connector
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
        print("✅ DB test query succeeded")
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

# Create tables
async def create_tables():
    try:
        async with engine.begin() as conn:
            print("🔍 Debug: Running create_all on Base metadata")
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
