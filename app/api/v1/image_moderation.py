from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.schemas.image import ImageAnalysisResponse, ImageModerationResult, ImageUploadResponse
from app.services.file_storage import FileStorageService


router = APIRouter()
file_storage = FileStorageService()

@router.post("/image", status_code=202, response_model=ImageAnalysisResponse)
async def moderate_image(
    file: UploadFile = File(...),
    source_id: Optional[str] = None,
    settings = Depends(get_settings)
):
    try:
        if not source_id:
            source_id = f"img-{uuid.uuid4().hex[:8]}"
            
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        file_content = await file.read()

        file_path, file_metadata = file_storage.save_uploaded_file(file_content, file.filename or "uploaded_image")

        task = celery_app.send_task(
            "tasks.image.scan",
            args=[file_path, source_id, file_metadata]
        )

        return ImageUploadResponse(
            task_id=task.id,
            file_info=file_metadata
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/image/{task_id}", response_model=ImageModerationResult)
async def get_image_moderation_result(task_id: str):

    try:
        result = celery_app.AsyncResult(task_id)

        if result.result is None:
            return ImageModerationResult(status="pending")
        
        task_result = result.result

        if isinstance(task_result, dict):
            return ImageModerationResult(**task_result)
        
        else:
            return ImageModerationResult(
                status="error",
                verdict="error",
                scores={},
                analysis={"error": "Invalid task result format"}
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get result: {str(e)}")