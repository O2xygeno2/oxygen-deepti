import os
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = quote_plus(os.getenv("DB_PASS", ""))  # safely handle None
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DATABASE_HOST")  # stays same because you set it correctly
DB_PORT = os.getenv("DATABASE_PORT", "5432")

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@/{DB_NAME}?host={DB_HOST}"
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create session factory
async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
