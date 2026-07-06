from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import traceback

from config import config
from database import get_db, engine, Base
from models import User, Log
from schemas import (
    UserCreate, UserLogin, UserResponse, Token, LogResponse, ErrorResponse
)
from crud import (
    create_user, get_user_by_username, get_user_by_email,
    get_all_users, create_log, get_logs
)
from auth import authenticate_user, get_current_user
from utils import create_access_token
from exceptions import (
    UserAlreadyExistsException, InvalidCredentialsException,
    ValidationException
)
from logger_setup import logger

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="AI Code Reviewer API with authentication and logging"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for all unhandled exceptions"""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "endpoint": request.url.path,
            "method": request.method,
        }
    )
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if config.DEBUG else "An unexpected error occurred",
            "error_type": type(exc).__name__
        }
    )

# Health check endpoint
@app.get("/", tags=["Health"])
async def read_root():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return {
        "status": "success",
        "message": "AI Code Reviewer Backend is running",
        "version": config.API_VERSION
    }

# ==================== Authentication Endpoints ====================

@app.post("/api/auth/register", response_model=UserResponse, tags=["Authentication"])
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    - **username**: Unique username
    - **email**: Valid email address
    - **password**: Password (will be hashed)
    """
    logger.info(f"User registration attempt: {user.username}")
    
    # Check if user already exists
    if get_user_by_username(db, user.username):
        logger.warning(f"Registration failed: Username already exists - {user.username}")
        raise UserAlreadyExistsException()
    
    if get_user_by_email(db, user.email):
        logger.warning(f"Registration failed: Email already exists - {user.email}")
        raise UserAlreadyExistsException()
    
    # Create new user
    db_user = create_user(db, user)
    logger.info(f"User registered successfully: {db_user.username} (ID: {db_user.id})")
    
    return db_user

@app.post("/api/auth/login", response_model=Token, tags=["Authentication"])
async def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login user and get access token
    
    - **username**: User's username
    - **password**: User's password
    
    Returns JWT access token
    """
    logger.info(f"Login attempt: {user.username}")
    
    # Authenticate user
    authenticated_user = authenticate_user(db, user.username, user.password)
    
    if not authenticated_user:
        logger.warning(f"Login failed: Invalid credentials for {user.username}")
        raise InvalidCredentialsException()
    
    # Create access token
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": authenticated_user.id},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in successfully: {authenticated_user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": authenticated_user
    }

# ==================== User Endpoints ====================

@app.get("/api/users/me", response_model=UserResponse, tags=["Users"])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's information
    
    Requires valid JWT token in Authorization header
    """
    logger.info(f"User info requested: {current_user.username}")
    return current_user

@app.get("/api/users", response_model=List[UserResponse], tags=["Users"])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all users with pagination
    
    Requires valid JWT token in Authorization header
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return (max 100)
    """
    logger.info(f"Users list requested by: {current_user.username}")
    users = get_all_users(db, skip=skip, limit=limit)
    return users

@app.get("/api/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID
    
    Requires valid JWT token in Authorization header
    """
    logger.info(f"User info requested by {current_user.username} for user {user_id}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

# ==================== Logging Endpoints ====================

@app.post("/api/logs", response_model=LogResponse, tags=["Logs"])
async def create_log_entry(
    log_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a log entry
    
    Requires valid JWT token in Authorization header
    """
    logger.info(f"Log entry created by: {current_user.username}")
    
    log_data["user_id"] = current_user.id
    db_log = create_log(db, log_data)
    
    return db_log

@app.get("/api/logs", response_model=List[LogResponse], tags=["Logs"])
async def get_logs_endpoint(
    skip: int = 0,
    limit: int = 100,
    level: str = None,
    user_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get logs with optional filtering
    
    Requires valid JWT token in Authorization header
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return (max 100)
    - **level**: Filter by log level (INFO, WARNING, ERROR, DEBUG, etc.)
    - **user_id**: Filter by user ID
    """
    logger.info(f"Logs requested by: {current_user.username}")
    
    logs = get_logs(
        db,
        user_id=user_id,
        level=level,
        skip=skip,
        limit=limit
    )
    
    return logs

@app.get("/api/logs/user/{user_id}", response_model=List[LogResponse], tags=["Logs"])
async def get_user_logs(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get logs for a specific user
    
    Requires valid JWT token in Authorization header
    """
    logger.info(f"User logs requested by {current_user.username} for user {user_id}")
    
    logs = get_logs(db, user_id=user_id, skip=skip, limit=limit)
    return logs

# ==================== Code Review Endpoint ====================

@app.post("/api/review", tags=["Code Review"])
async def review_code(
    code_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit code for AI review
    
    Requires valid JWT token in Authorization header
    """
    logger.info(f"Code review requested by: {current_user.username}")
    
    return {
        "status": "success",
        "message": "Code submitted for review",
        "review": "This is a mock AI code review. Integration with AI model pending.",
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting application on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=config.DEBUG)
