from typing import List
from celery import current_task
from app.celery_app import celery_app
from app.database import SessionLocal
from app.indexing import index_paragraphs_sync

@celery_app.task(bind=True)
def index_paragraphs(self, user_id: str, paragraph_ids: List[str]):
    """Celery task to index paragraphs in background"""
    db = SessionLocal()
    try:
        # Update task state
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': len(paragraph_ids), 'status': 'Starting indexing...'}
        )
        
        # Perform indexing
        index_paragraphs_sync(db, user_id, paragraph_ids)
        
        # Update task state
        current_task.update_state(
            state='SUCCESS',
            meta={'current': len(paragraph_ids), 'total': len(paragraph_ids), 'status': 'Indexing completed'}
        )
        
        return {'status': 'completed', 'indexed_paragraphs': len(paragraph_ids)}
        
    except Exception as exc:
        current_task.update_state(
            state='FAILURE',
            meta={'current': 0, 'total': len(paragraph_ids), 'status': str(exc)}
        )
        raise exc
    finally:
        db.close()
