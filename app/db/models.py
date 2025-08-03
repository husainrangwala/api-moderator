from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

# 1. Base class for all models
Base = declarative_base()

# 2. Example moderation event model
class ModerationEvent(Base):
    __tablename__ = "moderation_events"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False, index=True)      # e.g. "text" or "image"
    item_id = Column(String, nullable=False)                  # unique identifier for the content
    verdict = Column(String, nullable=False)                  # "clean" or "flagged"
    scores = Column(JSONB, nullable=False, default={})        # JSONB for category scores
    created_at = Column(DateTime(timezone=True), server_default=func.now())
