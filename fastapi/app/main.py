from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import async_session, engine
from app import models

app = FastAPI()

# Ensure tables are created at startup
@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
    except Exception as e:
        print("Warning: Could not connect to DB on startup:", e)


# Dependency for DB session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.get("/")
async def read_root(db: AsyncSession = Depends(get_db)):
    return {"msg": "FastAPI on Cloud Run with async PostgreSQL!"}
