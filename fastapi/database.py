import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from google.cloud.sql.connector import Connector

logger = logging.getLogger("database")

class Base(DeclarativeBase):
    pass

# Connector instance
connector = Connector()

# Fetch env vars
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
CLOUD_SQL_CONNECTION_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME")

async def get_connection():
    logger.info("🔍 DB connection variables:")
    logger.info(f"  DB_USER={DB_USER}")
    logger.info(f"  DB_PASSWORD={'*' * len(DB_PASSWORD) if DB_PASSWORD else 'NOT SET'}")
    logger.info(f"  DB_NAME={DB_NAME}")
    logger.info(f"  DB_HOST={DB_HOST}")
    logger.info(f"  DB_PORT={DB_PORT}")
    logger.info(f"  CLOUD_SQL_CONNECTION_NAME={CLOUD_SQL_CONNECTION_NAME}")

    try:
        conn = await connector.connect_async(
            CLOUD_SQL_CONNECTION_NAME,
            driver="asyncpg",
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            host=DB_HOST,
            port=int(DB_PORT)
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
            logger.info("🔍 Running test query: SELECT 1")
            await conn.execute("SELECT 1")
        logger.info("✅ DB test query succeeded")
        return True
    except Exception as e:
        logger.exception("❌ Database connection error")
        return False

# Create tables
async def create_tables():
    try:
        async with engine.begin() as conn:
            logger.info("🔍 Running Base.metadata.create_all")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tables created successfully")
    except Exception as e:
        logger.exception("❌ Failed to create tables")
