import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Database-agnostic UUID type
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa

class UUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    paragraphs = relationship("Paragraph", back_populates="user", cascade="all, delete-orphan")
    word_counts = relationship("WordCount", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

class Paragraph(Base):
    __tablename__ = "paragraphs"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="paragraphs")
    word_counts = relationship("ParagraphWordCount", back_populates="paragraph", cascade="all, delete-orphan")

class WordCount(Base):
    """Global word counts per user"""
    __tablename__ = "word_counts"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id"), nullable=False)
    word = Column(String(100), nullable=False)
    count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="word_counts")
    
    # Indexes for fast search
    __table_args__ = (
        Index('ix_word_counts_user_word', 'user_id', 'word'),
        Index('ix_word_counts_user_word_count', 'user_id', 'word', 'count'),
    )

class ParagraphWordCount(Base):
    """Word counts per paragraph per user"""
    __tablename__ = "paragraph_word_counts"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id"), nullable=False)
    paragraph_id = Column(UUID(), ForeignKey("paragraphs.id"), nullable=False)
    word = Column(String(100), nullable=False)
    count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    paragraph = relationship("Paragraph", back_populates="word_counts")
    
    # Indexes for fast search
    __table_args__ = (
        Index('ix_paragraph_word_counts_user_word', 'user_id', 'word'),
        Index('ix_paragraph_word_counts_user_word_count', 'user_id', 'word', 'count'),
        Index('ix_paragraph_word_counts_paragraph', 'paragraph_id'),
    )
