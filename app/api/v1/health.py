from fastapi import APIRouter

from app.schemas.health import HealthResponse


router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")