from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from models import User
from database import get_db
from utils import verify_token, hash_password, verify_password
from exceptions import InvalidTokenException
from logger_setup import logger

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token"""
    token = credentials.credentials
    
    payload = verify_token(token)
    if payload is None:
        logger.warning(f"Invalid token attempt: {token[:20]}...")
        raise InvalidTokenException()
    
    user_id = payload.get("sub")
    if user_id is None:
        logger.warning("Token missing user ID")
        raise InvalidTokenException()
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning(f"User not found for token: {user_id}")
        raise InvalidTokenException()
    
    if not user.is_active:
        logger.warning(f"Inactive user attempted login: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return user

def authenticate_user(db: Session, username: str, password: str) -> User:
    """Authenticate user by username and password"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        logger.info(f"Login attempt with non-existent username: {username}")
        return None
    
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Failed login attempt for user: {username}")
        return None
    
    return user
