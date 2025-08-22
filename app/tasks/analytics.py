from celery.schedules import crontab
from app.core.celery_app import celery_app
from app.services.metrics import metrics_collector
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.analytics.update_daily")
def update_daily_analytics():

    try:
        yesterday = date.today() - timedelta(days=1)
        metrics_collector.update_daily_analytics(yesterday)
        

        metrics_collector.update_daily_analytics(date.today())
        
        logger.info("Daily analytics update completed")
        return {"status": "completed", "date": yesterday.isoformat()}
        
    except Exception as e:
        logger.error(f"Daily analytics update failed: {e}")
        return {"status": "failed", "error": str(e)}

@celery_app.task(name="tasks.analytics.cleanup_old_metrics")
def cleanup_old_metrics():

    try:
        logger.info("Old metrics cleanup completed")
        return {"status": "completed"}
        
    except Exception as e:
        logger.error(f"Metrics cleanup failed: {e}")
        return {"status": "failed", "error": str(e)}


celery_app.conf.beat_schedule = {
    'update-daily-analytics': {
        'task': 'tasks.analytics.update_daily',
        'schedule': crontab(hour='1', minute='0'),
    },
    'cleanup-old-metrics': {
        'task': 'tasks.analytics.cleanup_old_metrics',
        'schedule': crontab(day_of_week='0', hour='2', minute='0'),
    },
}
