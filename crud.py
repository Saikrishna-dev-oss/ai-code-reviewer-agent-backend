from sqlalchemy.orm import Session
from models import User, Log
from schemas import UserCreate
from utils import hash_password
from datetime import datetime
from typing import List

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> User:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> User:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()

def create_log(db: Session, log_data: dict) -> Log:
    """Create a log entry"""
    db_log = Log(**log_data)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs(
    db: Session,
    user_id: int = None,
    level: str = None,
    skip: int = 0,
    limit: int = 100
) -> List[Log]:
    """Get logs with optional filtering"""
    query = db.query(Log)
    
    if user_id:
        query = query.filter(Log.user_id == user_id)
    
    if level:
        query = query.filter(Log.level == level)
    
    return query.order_by(Log.timestamp.desc()).offset(skip).limit(limit).all()
