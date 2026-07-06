import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./ai_code_reviewer.db"
    )
    
    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # API
    API_TITLE = "AI Code Reviewer API"
    API_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False") == "True"
    
    # CORS
    CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

config = Config()
