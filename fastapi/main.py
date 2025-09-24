from fastapi import FastAPI, Depends
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI with Cloud SQL", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    try:
        from database import test_connection, create_tables
        
        # Wait a bit for services to be ready
        await asyncio.sleep(2)
        
        if await test_connection():
            logger.info("✅ Database connection successful")
            await create_tables()
            logger.info("✅ Database tables ready")
        else:
            logger.error("❌ Database connection failed")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.get("/")
async def root():
    return {"message": "FastAPI with Cloud SQL"}

@app.get("/health")
async def health_check():
    try:
        from database import test_connection
        db_healthy = await test_connection()
        return {
            "status": "healthy" if db_healthy else "degraded",
            "database": "connected" if db_healthy else "disconnected",
            "service": "running"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "running"
        }

@app.get("/test-db")
async def test_db():
    from database import test_connection
    if await test_connection():
        return {"database": "connected"}
    else:
        return {"database": "disconnected"}
