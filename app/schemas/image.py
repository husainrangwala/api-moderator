from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    task_id: str
    file_info: Dict[str, Any]

class ImageModerationResult(BaseModel):
    status: Optional[str] = None
    verdict: Optional[str] = None
    scores: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    file_info: Optional[Dict[str, Any]] = None

class ImageAnalysisResponse(BaseModel):
    id: int
    moderation_event_id: int
    detected_objects: Optional[Dict[str, Any]]
    nsfw_score: Optional[Dict[str, Any]]
    text_in_image: Optional[str]
    processing_time: Optional[float]
    created_at: datetime
