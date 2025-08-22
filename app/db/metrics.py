from datetime import date, datetime, timedelta, timezone
import logging
from typing import Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import DailyAnalytics, ModerationEvent, SystemMetrics
from app.db.session import get_db_session



logger = logging.getLogger(__name__)

def create_system_metric(
        metric_name: str,
        metric_value: float,
        metric_unit: Optional[str] = None,
        metric_tags: Optional[Dict] = None,
        db: Optional[Session] = None
) -> SystemMetrics:
    
    should_close_db = False

    if db is None:
        db = get_db_session()
        should_close_db = True
    
    try:
        metric = SystemMetrics(
            metric_name,
            metric_value,
            metric_unit,
            metric_tags or {}
        )

        db.add(metric)
        db.flush()
        db.refresh(metric)
        db.commit()

        return metric
    
    except Exception as e:
        db.rollback()
        raise e
    
    finally:
        if should_close_db:
            db.close()

def upsert_daily_analytics(
        target_date: date,
        source_type: str,
        stats: Dict,
        db: Optional[Session] = None
) -> DailyAnalytics:
    
    should_close_db = False

    if db is None:
        db = get_db_session()
        should_close_db = True

    try:

        daily_record = db.query(DailyAnalytics).filter(
            DailyAnalytics.date == target_date,
            DailyAnalytics.source_type == source_type
        ).first()

        if daily_record:
            daily_record.total_requests = stats['total_requests']
            daily_record.flagged_count = stats['flagged_count']
            daily_record.clean_count = stats['clean_count']
            daily_record.error_count = stats['error_count']
            daily_record.avg_processing_time = stats['avg_processing_time']
            daily_record.total_file_size = stats['total_file_size']
            daily_record.updated_at = func.now()

        else:
            daily_record = DailyAnalytics(
                date = target_date,
                source_type = source_type,
                **stats
            )
            
            db.add(daily_record)
        
        db.commit()
        db.refresh(daily_record)

        return daily_record
    
    except Exception as e:
        db.rollback()
        raise e
    
    finally:
        if should_close_db:
            db.close()

def get_daily_analytics_by_date_and_source(
        target_date: date,
        source_type: str,
        db: Optional[Session] = None
) -> Optional[DailyAnalytics]:
    
    should_close_db = False

    if db is None:
        db = get_db_session()
        should_close_db = True

    try:
        return db.query(DailyAnalytics).filter(
            DailyAnalytics.date == target_date,
            DailyAnalytics.source_type == source_type
        ).first()
    
    finally:
        if should_close_db:
            db.close()

def get_moderation_events_by_date_and_source(
        target_date: date,
        source_type: str,
        db: Optional[Session] = None
) -> List[ModerationEvent]:
    
    should_close_db = False
    
    if not db:
        db = get_db_session()
        should_close_db = True
    
    try:
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=1)

        return db.query(ModerationEvent).filter(
            ModerationEvent.source == source_type,
            ModerationEvent.created_at >= start_datetime,
            ModerationEvent.created_at < end_datetime
        ).all()
    
    finally:
        if should_close_db:
            db.close()

def get_daily_analytics_range(
        start_date: date,
        end_date: date,
        db: Optional[Session] = None
) -> List[DailyAnalytics]:
    
    should_close_db = False

    if not db:
        db = get_db_session()
        should_close_db = True
    
    try:
        
        return db.query(DailyAnalytics).filter(
            DailyAnalytics.date >= start_date,
            DailyAnalytics.date <= end_date
        ).all()
    
    finally:
        if should_close_db:
            db.close()

def get_system_metrics_by_name_and_timeframe(
    metric_name: str,
    start_time: datetime,
    end_time: datetime,
    db: Optional[Session] = None
) -> List[SystemMetrics]:
    
    should_close_db = False
    
    if db is None:
        db = get_db_session()
        should_close_db = True
    
    try:
        return db.query(SystemMetrics).filter(
            SystemMetrics.metric_name == metric_name,
            SystemMetrics.timestamp >= start_time,
            SystemMetrics.timestamp <= end_time
        ).order_by(SystemMetrics.timestamp).all()
    
    finally:
        if should_close_db:
            db.close()