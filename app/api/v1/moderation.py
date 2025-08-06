from fastapi import APIRouter, Depends
from app.schemas.moderation import TextPayload, TaskResponse, TaskResult
from app.core.config import get_settings
from app.core.celery_app import celery_app

router = APIRouter()

@router.post("/text", status_code=202, response_model=TaskResponse)
async def moderate_text(item: TextPayload, settings: dict = Depends(get_settings)):
    task = celery_app.send_task("tasks.text.scan", args=[item.content, item.source_id])
    return TaskResponse(task_id=task.id)

@router.get("/task/{task_id}", response_model=TaskResult)
async def get_text_result(task_id: str):
    result = celery_app.AsyncResult(task_id).result
    if result:
        return TaskResult(verdict=result["verdict"], scores=result["scores"])
    return TaskResult(status="pending")