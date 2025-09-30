import os
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from google.cloud.sql.connector import Connector

logger = logging.getLogger("database")

class Base(DeclarativeBase):
    pass

# Connector instance
connector = Connector()

# Hardcoded values - CORRECTED
DB_USER = "fastapi-db-user"
DB_PASSWORD = "fastapiDB@12"
DB_NAME = "fastapi-db-name"
CLOUD_SQL_CONNECTION_NAME = "master-shell-468709-v8:asia-south1:fastapi-db"

async def get_connection():
    logger.info("🔍 DB connection variables:")
    logger.info(f"  DB_USER={DB_USER}")
    logger.info(f"  DB_PASSWORD={'*' * len(DB_PASSWORD) if DB_PASSWORD else 'NOT SET'}")
    logger.info(f"  DB_NAME={DB_NAME}")
    logger.info(f"  CLOUD_SQL_CONNECTION_NAME={CLOUD_SQL_CONNECTION_NAME}")

    try:
        # For Cloud SQL connector, only use connection_name, not host/port
        conn = await connector.connect_async(
            CLOUD_SQL_CONNECTION_NAME,  # This is the key parameter
            "asyncpg",  # driver
            user=DB_USER,
            password=DB_PASSWORD, 
            db=DB_NAME
            # Remove host and port - Cloud SQL connector handles this automatically
        )
        logger.info("✅ Successfully created async DB connection")
        return conn
    except Exception as e:
        logger.exception("❌ Failed to create DB connection")
        raise

# Engine
engine = create_async_engine(
    "postgresql+asyncpg://",
    async_creator=get_connection,
    echo=True,
    pool_pre_ping=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency
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
            # ✅ Wrap raw SQL in text()
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar_one()
            if value == 1:
                logger.info("✅ Database connection successful!")
            else:
                logger.error("❌ Unexpected result from DB")
    except Exception as e:
        logger.error("❌ Database connection error")
        logger.exception(e)


# Create tables
async def create_tables():
    try:
        async with engine.begin() as conn:
            logger.info("🔍 Running Base.metadata.create_all")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tables created successfully")
    except Exception as e:
        logger.exception("❌ Failed to create tables")
