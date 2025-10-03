from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import asyncio
import os
import time

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(title="FastAPI with Cloud SQL", version="1.0.0")

# Global variable to track startup status
startup_complete = False

# Import database modules after app creation to avoid circular imports
from database import get_db, test_connection, create_tables
from models import User, Post
from schemas import UserCreate, User as UserSchema

@app.on_event("startup")
async def startup_event():
    global startup_complete
    logger.info("🚀 Starting up application...")
    
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🔍 Attempt {attempt + 1}/{max_retries} to connect to database...")
            
            # Test database connection
            if await test_connection():
                logger.info("✅ Database connection successful")
                
                # Create tables
                if await create_tables():
                    logger.info("✅ Database tables ready")
                    startup_complete = True
                    logger.info("🎉 Startup completed successfully")
                    return
                else:
                    logger.error("❌ Failed to create tables")
            else:
                logger.error(f"❌ Database connection failed on attempt {attempt + 1}")
                
        except Exception as e:
            logger.exception(f"💥 Startup attempt {attempt + 1} failed: {e}")
        
        if attempt < max_retries - 1:
            logger.info(f"⏳ Waiting {retry_delay} seconds before retry...")
            await asyncio.sleep(retry_delay)
    
    logger.error("💥 All startup attempts failed")
    startup_complete = False

@app.get("/")
async def root():
    logger.info("📡 Root endpoint called")
    return {
        "message": "FastAPI with Cloud SQL", 
        "status": "running",
        "startup_complete": startup_complete
    }

@app.get("/health")
async def health_check():
    """Basic health check"""
    logger.info("📡 Health check endpoint called")
    return {
        "status": "running",
        "timestamp": time.time(),
        "startup_complete": startup_complete
    }

@app.get("/ready")
async def ready_check():
    """Startup probe endpoint - critical for Cloud Run"""
    logger.info("🔍 Startup probe check")
    
    if not startup_complete:
        logger.warning("⚠️ Service not ready - startup not complete")
        raise HTTPException(
            status_code=503, 
            detail="Service not ready - startup in progress"
        )
    
    # Test database connection
    try:
        db_healthy = await test_connection()
        if db_healthy:
            logger.info("✅ Ready check passed")
            return {"status": "ready", "database": "connected"}
        else:
            logger.error("❌ Ready check failed - database not connected")
            raise HTTPException(
                status_code=503, 
                detail="Database not connected"
            )
    except Exception as e:
        logger.exception(f"💥 Ready check error: {e}")
        raise HTTPException(
            status_code=503, 
            detail=f"Service not ready: {str(e)}"
        )

@app.get("/test-db")
async def test_db():
    """Detailed database test endpoint"""
    logger.info("📡 Test-DB endpoint called")
    try:
        db_healthy = await test_connection()
        return {
            "database": "connected" if db_healthy else "disconnected",
            "status": "success" if db_healthy else "error",
            "startup_complete": startup_complete
        }
    except Exception as e:
        logger.exception(f"Database test error: {e}")
        return {
            "database": "error",
            "status": "error",
            "error": str(e)
        }

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check environment and status"""
    return {
        "startup_complete": startup_complete,
        "environment_vars": {
            "DB_USER": bool(os.getenv("DB_USER")),
            "DB_NAME": bool(os.getenv("DB_NAME")),
            "DB_HOST": os.getenv("DB_HOST"),
            "CLOUD_SQL_CONNECTION_NAME": os.getenv("CLOUD_SQL_CONNECTION_NAME")
        },
        "timestamp": time.time()
    }

# User endpoints (only if startup is complete)
@app.post("/users/", response_model=UserSchema)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    if not startup_complete:
        raise HTTPException(status_code=503, detail="Service starting up")
    
    try:
        from sqlalchemy import insert
        from sqlalchemy.exc import IntegrityError
        
        stmt = insert(User).values(
            email=user.email,
            name=user.name
        ).returning(User)
        
        result = await db.execute(stmt)
        new_user = result.scalar_one()
        await db.commit()
        
        logger.info(f"✅ Created user: {new_user.email}")
        return new_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/", response_model=list[UserSchema])
async def get_users(db: AsyncSession = Depends(get_db)):
    if not startup_complete:
        raise HTTPException(status_code=503, detail="Service starting up")
    
    try:
        from sqlalchemy import select
        result = await db.execute(select(User))
        users = result.scalars().all()
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# This ensures the app variable is available when imported
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
