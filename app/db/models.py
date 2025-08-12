from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, Dict, Any

# 1. Base class for all models
Base = declarative_base()

class ModerationEvent(Base):
    __tablename__ = "moderation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String, nullable=False, index=True)
    item_id: Mapped[str] = mapped_column(String, nullable=False)
    verdict: Mapped[str] = mapped_column(String, nullable=False)
    scores: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default={})
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    file_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    image_dimensions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    image_analysis = relationship("ImageAnalysis", back_populates="moderation_event")

class ImageAnalysis(Base):
    __tablename__ = "image_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    moderation_event_id: Mapped[int] = mapped_column(Integer, ForeignKey("moderation_events.id"), nullable=False)
    detected_objects: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    nsfw_scores: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    text_in_image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    processing_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    moderation_event = relationship("ModerationEvent", back_populates="image_analysis")
