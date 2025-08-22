from datetime import datetime
from sqlalchemy import BigInteger, Date, Float, ForeignKey, Integer, String, DateTime, Text, func
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

    # Image support fields
    file_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    image_dimensions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Relationship
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
    
    # Relationship
    moderation_event = relationship("ModerationEvent", back_populates="image_analysis")

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    metric_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_unit: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metric_tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

class DailyAnalytics(Base):
    __tablename__ = "daily_analytics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    total_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    flagged_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clean_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_processing_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 
