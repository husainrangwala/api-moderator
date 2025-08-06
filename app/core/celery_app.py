from celery import Celery
from app.core.config import get_settings

settings = get_settings()
celery_app = Celery(
    "api_moderator",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.autodiscover_tasks(["app.tasks"])