from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import async_session
from app import models

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with async_session() as session:
        async with session.begin():
            await session.run_sync(models.Base.metadata.create_all)

async def get_db():
    async with async_session() as session:
        yield session

@app.get("/")
async def read_root():
    return {"msg": "FastAPI on Cloud Run with async PostgreSQL!"}
