from pydantic import BaseModel
from typing import Dict, Any, Optional

class TextPayload(BaseModel):
    content: str
    source_id: str

class ModerationResponse(BaseModel):
    verdict: str
    scores: Dict[str, Any]

class TaskResponse(BaseModel):
    task_id: str

class TaskResult(BaseModel):
    status: Optional[str] = None
    verdict: Optional[str] = None
    scores: Optional[Dict[str, Any]] = None
