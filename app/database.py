from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create engine based on configuration
if settings.USE_SQLITE:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}  # SQLite specific
    )
else:
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
