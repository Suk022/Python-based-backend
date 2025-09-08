import os
from typing import Optional

class Settings:
    """Application configuration settings"""
    
    # Database configuration
    USE_SQLITE: bool = os.getenv("USE_SQLITE", "false").lower() == "true"
    
    # SQLite database path for development
    SQLITE_URL: str = "sqlite:///./database.db"
    
    # PostgreSQL configuration for production deployment
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "backend_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "backend_db")
    
    @property
    def DATABASE_URL(self) -> str:
        if self.USE_SQLITE:
            return self.SQLITE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis configuration for background tasks
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT authentication settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Background task processing configuration
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL

settings = Settings()
