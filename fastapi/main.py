from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import asyncio
import os

from database import get_db, create_tables, test_connection
import models
import schemas

app = FastAPI(
    title="Async FastAPI with Cloud SQL PostgreSQL",
    description="High-performance async FastAPI application with Cloud SQL",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Starting up async FastAPI application...")
    
    # Test database connection
    if await test_connection():
        print("✅ Database connection successful")
        
        # Create tables
        await create_tables()
        print("✅ Database tables created/verified")
    else:
        print("❌ Database connection failed")

@app.get("/")
async def root():
    return {
        "message": "Async FastAPI with Cloud SQL PostgreSQL",
        "status": "running",
        "async": True
    }

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check"""
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": asyncio.get_event_loop().time()
    }

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user asynchronously"""
    # Check if user already exists
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[schemas.User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get users with pagination - fully async"""
    result = await db.execute(
        select(models.User)
        .offset(skip)
        .limit(limit)
        .order_by(models.User.created_at.desc())
    )
    users = result.scalars().all()
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific user by ID"""
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# Async batch operations example
@app.post("/users/batch/", response_model=list[schemas.User])
async def create_users_batch(users: list[schemas.UserCreate], db: AsyncSession = Depends(get_db)):
    """Create multiple users in batch - demonstrates async efficiency"""
    db_users = []
    for user_data in users:
        db_user = models.User(**user_data.model_dump())
        db.add(db_user)
        db_users.append(db_user)
    
    await db.commit()
    
    # Refresh all users
    for db_user in db_users:
        await db.refresh(db_user)
    
    return db_users

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        workers=int(os.getenv("WEB_CONCURRENCY", 1))
    )
