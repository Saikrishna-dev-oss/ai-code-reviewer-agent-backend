import logging
import logging.handlers
from config import config
from sqlalchemy.orm import Session
from models import Log
from datetime import datetime

class DatabaseHandler(logging.Handler):
    """Custom logging handler that stores logs in the database"""
    
    def __init__(self, db_session=None):
        super().__init__()
        self.db_session = db_session
    
    def emit(self, record: logging.LogRecord):
        try:
            if self.db_session is None:
                return
            
            log_entry = Log(
                level=record.levelname,
                logger_name=record.name,
                message=record.getMessage(),
                timestamp=datetime.utcnow()
            )
            
            # Extract exception info if present
            if record.exc_info:
                log_entry.exception_type = record.exc_info[0].__name__
                log_entry.exception_message = str(record.exc_info[1])
            
            self.db_session.add(log_entry)
            self.db_session.commit()
        except Exception:
            # Prevent logging errors from breaking the application
            pass

def setup_logger(name: str, db_session=None) -> logging.Logger:
    """Setup a logger with both file and database handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)
    console_formatter = logging.Formatter(config.LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        "app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(config.LOG_LEVEL)
    file_formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Database handler (if session provided)
    if db_session:
        db_handler = DatabaseHandler(db_session)
        db_handler.setLevel(config.LOG_LEVEL)
        logger.addHandler(db_handler)
    
    return logger

# Global logger
logger = logging.getLogger("ai_code_reviewer")
logger.setLevel(config.LOG_LEVEL)

console_handler = logging.StreamHandler()
console_handler.setLevel(config.LOG_LEVEL)
console_formatter = logging.Formatter(config.LOG_FORMAT)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

file_handler = logging.handlers.RotatingFileHandler(
    "app.log",
    maxBytes=10485760,
    backupCount=5
)
file_handler.setLevel(config.LOG_LEVEL)
file_formatter = logging.Formatter(config.LOG_FORMAT)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
