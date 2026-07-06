from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime
from database import Base

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Log(Base):
    """Log model for storing application logs"""
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)  # INFO, WARNING, ERROR, DEBUG, etc.
    logger_name = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    user_id = Column(Integer, nullable=True, index=True)
    endpoint = Column(String, nullable=True)
    method = Column(String, nullable=True)
    status_code = Column(Integer, nullable=True)
    exception_type = Column(String, nullable=True)
    exception_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
