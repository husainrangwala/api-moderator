from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import get_settings
from app.services.metrics import metrics_collector


router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(7, ge=1, le=30),
    settings = Depends(get_settings)
) -> Dict[str, Any]:
    
    try:
        summary = metrics_collector.get_metrics_summary(days)
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")
    

@router.get("/metrics/{metric_name}")
async def get_metric_history(
    metric_name: str,
    hours: int = Query(24, ge=1, le=168),
    settings = Depends(get_settings)
):
    try:
        return {
            "metric_name": metric_name,
            "period": f'Last {hours} hours',
            "data": []
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metric history: {str(e)}")
    
