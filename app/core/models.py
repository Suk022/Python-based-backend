from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    paragraphs = relationship("Paragraph", back_populates="user", cascade="all, delete-orphan")
    word_counts = relationship("WordCount", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

class Paragraph(Base):
    __tablename__ = "paragraphs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="paragraphs")
    word_counts = relationship("ParagraphWordCount", back_populates="paragraph", cascade="all, delete-orphan")

class WordCount(Base):
    """Global word counts per user"""
    __tablename__ = "word_counts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
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
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paragraph_id = Column(Integer, ForeignKey("paragraphs.id"), nullable=False)
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
