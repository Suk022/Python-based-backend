import re
from collections import Counter
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import Paragraph, WordCount, ParagraphWordCount

def tokenize_text(text: str) -> List[str]:
    """Tokenize text into words (lowercase, remove punctuation)"""
    # Use regex to find words (letters, numbers, apostrophes)
    words = re.findall(r"[A-Za-z0-9']+", text.lower())
    return words

def index_paragraphs_sync(db: Session, user_id: str, paragraph_ids: List[str]):
    """Synchronously index paragraphs for word counts"""
    try:
        # Get paragraphs to index
        paragraphs = db.query(Paragraph).filter(
            Paragraph.id.in_(paragraph_ids),
            Paragraph.user_id == user_id
        ).all()
        
        # Process each paragraph
        for paragraph in paragraphs:
            words = tokenize_text(paragraph.content)
            word_counts = Counter(words)
            
            # Update paragraph word counts
            for word, count in word_counts.items():
                # Check if record exists
                existing = db.query(ParagraphWordCount).filter(
                    ParagraphWordCount.user_id == user_id,
                    ParagraphWordCount.paragraph_id == paragraph.id,
                    ParagraphWordCount.word == word
                ).first()
                
                if existing:
                    existing.count = count
                else:
                    new_count = ParagraphWordCount(
                        user_id=user_id,
                        paragraph_id=paragraph.id,
                        word=word,
                        count=count
                    )
                    db.add(new_count)
            
            # Update global word counts
            for word, count in word_counts.items():
                # Check if global word count exists
                existing_global = db.query(WordCount).filter(
                    WordCount.user_id == user_id,
                    WordCount.word == word
                ).first()
                
                if existing_global:
                    existing_global.count += count
                else:
                    new_global_count = WordCount(
                        user_id=user_id,
                        word=word,
                        count=count
                    )
                    db.add(new_global_count)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e
