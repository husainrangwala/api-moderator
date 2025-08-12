from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.db.models import ImageAnalysis, ModerationEvent
from app.db.session import get_db_session

def save_event(
        source: str,
        item_id: str,
        verdict: str,
        scores: Dict[str, Any],
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        file_type: Optional[str] = None,
        image_dimensions: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
) -> ModerationEvent:
    
    should_close_db = False

    if db is None:
        from app.db.session import get_db_session
        db = get_db_session()
        should_close_db = True
    
    try:
        event = ModerationEvent(
            source=source,
            item_id=item_id,
            verdict=verdict,
            scores=scores,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            image_dimensions=image_dimensions
        )

        db.add(event)
        db.flush()
        db.refresh(event)
        db.commit()

        return event

    except Exception as e:
        db.rollback()
        raise e

    finally:
        if should_close_db:
            db.close()
    

def get_event_by_id(event_id: int, db: Optional[Session] = None) -> Optional[ModerationEvent]:
    should_close_db = False

    if db is None:
        from app.db.session import get_db_session
        db = get_db_session()
        should_close_db = True
    
    try:
        return db.query(ModerationEvent).filter(ModerationEvent.id == event_id).first()
    
    finally:
        if should_close_db:
            db.close()


def get_event_by_source_id(item_id: str, db: Optional[Session] = None) -> list[ModerationEvent]:
    should_close_db = False

    if db is None:
        from app.db.session import get_db_session
        db = get_db_session()
        should_close_db = True
    
    try:
        return db.query(ModerationEvent).filter(ModerationEvent.item_id == item_id).all()
    
    finally:
        if should_close_db:
            db.close()


def save_image_analysis(
        moderation_event_id: int,
    detected_objects: Optional[Dict[str, Any]] = None,
    nsfw_scores: Optional[Dict[str, Any]] = None,
    text_in_image: Optional[str] = None,
    image_hash: Optional[str] = None,
    processing_time: Optional[float] = None,
    db: Optional[Session] = None
) -> ImageAnalysis:
    
    should_close_db = False

    if db is None:
        db = get_db_session()
        should_close_db = True

    try:
        analysis = ImageAnalysis(
            moderation_event_id=moderation_event_id,
            detected_objects=detected_objects,
            nsfw_scores=nsfw_scores,
            text_in_image=text_in_image,
            image_hash=image_hash,
            processing_time=processing_time
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return analysis
    
    except Exception as e:
        db.rollback()
        raise e
    
    finally:
        if should_close_db:
            db.close()