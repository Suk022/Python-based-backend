from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr  #EmailStr pydantic type for email validation
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    email: Optional[str] = None

# User schemas
class UserBase(BaseModel):
    email: str

class User(UserBase):
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Paragraph schemas
class ParagraphCreate(BaseModel):
    paragraphs: List[str]

class ParagraphResponse(BaseModel):
    id: uuid.UUID
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ParagraphList(BaseModel):
    paragraphs: List[ParagraphResponse]
    total: int
    page: int
    per_page: int

# Search schemas
class SearchResult(BaseModel):
    paragraph_id: uuid.UUID
    content: str
    word_count: int
    created_at: datetime

class SearchResponse(BaseModel):
    word: str
    results: List[SearchResult]
    total_found: int
