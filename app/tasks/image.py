import logging
import time

from app.core.celery_app import celery_app
from app.db.crud import save_event, save_image_analysis
from app.services.file_storage import FileStorageService
from app.services.image_analyzer import ImageAnalyzer


logger = logging.getLogger(__name__)
file_storage = FileStorageService()

@celery_app.task(name="tasks.image.scan", bind=True, max_retries=3, default_retry_delay = 60)
def scan_image(self, image_path: str, source_id: str, file_metadata: dict):

    start_time = time.time()

    try:
        logger.info(f"Starting image moderation for source_id: {source_id}")

        analyzer = ImageAnalyzer()

        verdict, analysis_data = analyzer.analyze_image(image_path)
        processing_time = time.time() - start_time

        try:
            from app.db.session import get_db_session
            db = get_db_session()

            moderation_event = save_event(
                source="image",
                item_id=source_id,
                verdict=verdict,
                scores=analysis_data.get('nsfw_scores', {}),
                file_path=image_path,
                file_size=file_metadata.get('file_size'),
                file_type=file_metadata.get('file_type'),
                image_dimensions=file_metadata.get('dimensions', {}),
                db=db
            )

            image_analysis = save_image_analysis(
                moderation_event_id=moderation_event.id,
                detected_objects=analysis_data.get('detected_objects'),
                nsfw_scores=analysis_data.get('nsfw_scores'),
                text_in_image=analysis_data.get('extracted_text'),
                image_hash=file_metadata.get('file_hash'),
                processing_time=processing_time,
                db=db
            )

            logger.info(f"Saved image moderation event with ID: {moderation_event.id}")
            db.close()
            
        except Exception as db_error:
            if 'db' in locals():
                db.rollback()
                db.close()
            logger.error(f"Database error: {db_error}")

        result = {
            "verdict": verdict,
            "scores": analysis_data.get('nsfw_scores', {}),
            "analysis": analysis_data,
            "file_info": file_metadata,
            "source_id": source_id,
            "processing_time": processing_time
        }
        
        logger.info(f"Completed image moderation: {verdict} for {source_id} in {processing_time:.2f}s")
        return result
    
    except Exception as exc:
        logger.error(f"Image moderation task failed: {exc}")
        
        try:
            file_storage.delete_file(image_path)
        except:
            pass

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying image task (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60, exc=exc)
        
        return {
            "verdict": "error",
            "scores": {},
            "analysis": {"error": str(exc)},
            "file_info": file_metadata,
            "source_id": source_id,
            "error": str(exc)
        }