from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import async_session, engine
from app import models

app = FastAPI()

# Ensure tables are created at startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Dependency for DB session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.get("/")
async def read_root(db: AsyncSession = Depends(get_db)):
    return {"msg": "FastAPI on Cloud Run with async PostgreSQL!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
