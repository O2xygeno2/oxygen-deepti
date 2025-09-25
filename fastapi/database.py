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

    # Debug: print environment variables
    db_user = os.getenv("DB_USER", "fastapi-db-user")
    db_password = os.getenv("DB_PASSWORD", "fastapiDB@12")
    db_name = os.getenv("DB_NAME", "fastapi-db-name")
    instance_conn_name = "master-shell-468709-v8:asia-south1:fastapi-db"

    print("🔍 Debug: DB connection variables")
    print(f"  DB_USER: {db_user}")
    print(f"  DB_PASSWORD: {'*' * len(db_password) if db_password else 'NOT SET'}")  # hide actual password
    print(f"  DB_NAME: {db_name}")
    print(f"  INSTANCE_CONNECTION_NAME: {instance_conn_name}")

    try:
        connection = await connector.connect_async(
            instance_conn_name,
            "asyncpg",
            user=db_user,
            password=db_password,
            db=db_name
        )
        print("✅ Debug: Successfully created async connection object")
        return connection
    except Exception as e:
        print(f"❌ Debug: Failed to create DB connection: {e}")
        raise

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
            print("🔍 Debug: Testing DB connection with SELECT 1")
            await conn.execute("SELECT 1")
        print("✅ Debug: DB test query succeeded")
        return True
    except Exception as e:
        print(f"❌ Debug: Database connection error: {e}")
        return False

async def create_tables():
    try:
        async with engine.begin() as conn:
            print("🔍 Debug: Running create_all on Base metadata")
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Debug: Tables created successfully")
    except Exception as e:
        print(f"❌ Debug: Failed to create tables: {e}")
