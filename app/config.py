import os

class Settings:
    """Application configuration settings"""
    
    # Database configuration - SQLite only for simplicity
    DATABASE_URL: str = "sqlite:///./database.db"
    
    # JWT authentication settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

settings = Settings()
