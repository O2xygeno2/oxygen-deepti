import os
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DATABASE_USER")
DB_PASS = quote_plus(os.getenv("DATABASE_PASSWORD"))  # encode special chars
DB_NAME = os.getenv("DATABASE_NAME")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@/{DB_NAME}"
    f"?host=/cloudsql/{INSTANCE_CONNECTION_NAME}"
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create session factory
async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
