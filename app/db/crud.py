from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.db.models import ModerationEvent

def save_event(
        source: str,
        item_id: str,
        verdict: str,
        scores: Dict[str, Any],
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
            scores=scores
        )

        db.add(event)
        db.commit()
        db.refresh(event)

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


def get_event_by_source_id(item_id: int, db: Optional[Session] = None) -> list[ModerationEvent]:
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

