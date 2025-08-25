import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}"
    f"@/{os.getenv('DATABASE_NAME')}?host={os.getenv('DATABASE_HOST')}"
)
postgresql+asyncpg://deepti-db:DeeptiGarg0111!@/appdb?host=/cloudsql/master-shell-468709-v8:asia-south1:oxygen-db-instance

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create session factory
async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
