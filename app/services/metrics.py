from app.db import metrics as metrics_db
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Optional, cast
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    def _calculate_daily_stats(self, target_date: date, source_type: str) -> Dict:

        try:
            events = metrics_db.get_moderation_events_by_date_and_source(target_date, source_type)
            
            total_requests = len(events)
            flagged_count = sum(1 for e in events if e.verdict == 'flagged')
            clean_count = sum(1 for e in events if e.verdict == 'clean')
            error_count = sum(1 for e in events if e.verdict == 'error')
            
            avg_processing_time = None
            
            total_file_size = None
            if source_type == 'image':
                total_file_size = sum(e.file_size or 0 for e in events)
            
            return {
                'total_requests': total_requests,
                'flagged_count': flagged_count,
                'clean_count': clean_count,
                'error_count': error_count,
                'avg_processing_time': avg_processing_time,
                'total_file_size': total_file_size
            }
        
        except Exception as e:
            logger.error(f"Failed to calculate daily stats: {e}")
            return {
                'total_requests': 0,
                'flagged_count': 0,
                'clean_count': 0,
                'error_count': 0,
                'avg_processing_time': None,
                'total_file_size': None
            }
    
    def record_metric(
        self, 
        metric_name: str, 
        value: float, 
        unit: Optional[str] = None, 
        tags: Optional[Dict] = None
    ):
        
        try:
            metrics_db.create_system_metric(
                metric_name=metric_name,
                metric_value=value,
                metric_unit=unit,
                metric_tags=tags
            )
            logger.debug(f"Recorded metric: {metric_name} = {value}")
        except Exception as e:
            logger.error(f"Failed to record metric {metric_name}: {e}")

    def update_daily_analytics(self, target_date: Optional[date] = None):

        if target_date is None:
            target_date = date.today()
        
        try:
            for source_type in ['text', 'image']:

                stats = self._calculate_daily_stats(target_date, source_type)
                
                metrics_db.upsert_daily_analytics(target_date, source_type, stats)
                
            logger.info(f"Updated daily analytics for {target_date}")
            
        except Exception as e:
            logger.error(f"Failed to update daily analytics: {e}")

    def get_metrics_summary(self, days: int = 7) -> Dict:
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            daily_stats = metrics_db.get_daily_analytics_range(start_date, end_date)
            
            summary = {
                'period': f'Last {days} days',
                'total_requests': sum(s.total_requests for s in daily_stats),
                'by_source': {},
                'by_verdict': {
                    'flagged': sum(s.flagged_count for s in daily_stats),
                    'clean': sum(s.clean_count for s in daily_stats),
                    'error': sum(s.error_count for s in daily_stats)
                },
                'daily_breakdown': []
            }
            
            for source_type in ['text', 'image']:
                source_stats = [s for s in daily_stats if s.source_type == source_type]
                summary['by_source'][source_type] = {
                    'total_requests': sum(s.total_requests for s in source_stats),
                    'flagged': sum(s.flagged_count for s in source_stats),
                    'clean': sum(s.clean_count for s in source_stats),
                    'error': sum(s.error_count for s in source_stats)
                }
            
            for single_date in (start_date + timedelta(n) for n in range(days)):
                day_stats = [s for s in daily_stats if s.date == single_date]
                summary['daily_breakdown'].append({
                    'date': single_date.isoformat(),
                    'total_requests': sum(s.total_requests for s in day_stats),
                    'flagged': sum(s.flagged_count for s in day_stats),
                    'clean': sum(s.clean_count for s in day_stats),
                    'error': sum(s.error_count for s in day_stats)
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {'error': str(e)}

    def get_metric_history(self, metric_name: str, hours: int = 24) -> Dict:
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            metrics = metrics_db.get_system_metrics_by_name_and_timeframe(
                metric_name, start_time, end_time
            )
            
            return {
                'metric_name': metric_name,
                'period': f'Last {hours} hours',
                'data': [
                    {
                        'timestamp': cast(datetime, m.timestamp).isoformat(),
                        'value': m.metric_value,
                        'unit': m.metric_unit,
                        'tags': m.metric_tags
                    }
                    for m in metrics
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get metric history for {metric_name}: {e}")
            return {'error': str(e)}

metrics_collector = MetricsCollector()