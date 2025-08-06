import logging

from app.core.celery_app import celery_app
from app.db.crud import save_event
from app.services.openai_client import check_text


logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.text.scan", bind=True, max_retries=3, default_retry_delay=60)
def scan_text(self, content: str, source_id: str):
    try:
        logger.info(f"Starting text moderation for source_id: {source_id}")

        if not content.strip():
            verdict, scores = "clean", {}
        else:
            verdict, scores = check_text(content)

        try:
            event = save_event("text", source_id, verdict, scores)
            logger.info(f"Saved Moderation event with ID: {event.id}")

        except Exception as db_error:
            logger.error(f"Database error {db_error}")
        
        result = {
            "verdict": verdict,
            "scores": scores,
            "source_id": source_id,
            "content_length": len(content)
        }

        logger.info(f"Completed text moderation: {result[verdict]} for {source_id}")

        return result
    
    except Exception as e:
        logger.error(f"Task failed: {e}")

        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task attempt {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)

        return {
            "verdict": "error",
            "scores": {},
            "source_id": source_id,
            "error": str(e)
        }