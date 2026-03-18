from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.dependencies import get_current_user
from app.core.models import User, Paragraph, ParagraphWordCount
from app.core.schemas import ParagraphCreate, ParagraphResponse, ParagraphList, SearchResponse, SearchResult
from app.services.indexing import index_paragraphs_sync

router = APIRouter(prefix="/paragraphs", tags=["paragraphs"])

@router.post("/", response_model=dict)
async def create_paragraphs(
    paragraph_data: ParagraphCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit multiple paragraphs and trigger indexing"""
    if not paragraph_data.paragraphs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one paragraph is required"
        )
    
    # Create paragraph records
    created_paragraphs = []
    for content in paragraph_data.paragraphs:
        if content.strip():  # Only create non-empty paragraphs
            paragraph = Paragraph(
                user_id=current_user.id,
                content=content.strip()
            )
            db.add(paragraph)
            created_paragraphs.append(paragraph)
    
    db.commit()
    
    # Refresh to get IDs
    for paragraph in created_paragraphs:
        db.refresh(paragraph)
    
    paragraph_ids = [p.id for p in created_paragraphs]
    
    # Trigger background indexing
    background_tasks.add_task(
        index_paragraphs_sync, 
        db, 
        current_user.id, 
        paragraph_ids
    )
    
    return {
        "message": f"Created {len(created_paragraphs)} paragraphs",
        "paragraph_ids": paragraph_ids,
        "indexing_status": "queued"
    }

@router.get("/", response_model=ParagraphList)
async def get_paragraphs(
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's paragraphs with pagination"""
    if page < 1 or per_page < 1 or per_page > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pagination parameters"
        )
    
    # Get total count
    total = db.query(Paragraph).filter(Paragraph.user_id == current_user.id).count()
    
    # Get paginated results
    paragraphs = (
        db.query(Paragraph)
        .filter(Paragraph.user_id == current_user.id)
        .order_by(desc(Paragraph.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    
    return ParagraphList(
        paragraphs=paragraphs,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/search", response_model=SearchResponse)
async def search_paragraphs(
    word: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for paragraphs containing a word, ranked by frequency"""
    if not word or not word.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search word is required"
        )
    
    search_word = word.strip().lower()
    
    # Query for paragraphs with word counts, ordered by count descending
    results = (
        db.query(
            ParagraphWordCount.paragraph_id,
            ParagraphWordCount.count,
            Paragraph.content,
            Paragraph.created_at
        )
        .join(Paragraph, ParagraphWordCount.paragraph_id == Paragraph.id)
        .filter(
            ParagraphWordCount.user_id == current_user.id,
            ParagraphWordCount.word == search_word
        )
        .order_by(desc(ParagraphWordCount.count))
        .limit(10)
        .all()
    )
    
    search_results = [
        SearchResult(
            paragraph_id=result.paragraph_id,
            content=result.content,
            word_count=result.count,
            created_at=result.created_at
        )
        for result in results
    ]
    
    return SearchResponse(
        word=search_word,
        results=search_results,
        total_found=len(search_results)
    )
