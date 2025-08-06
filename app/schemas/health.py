from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str

class DetailedHealthResponse(BaseModel):
    status: str
    version: str
    environment: str
