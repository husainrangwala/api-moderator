from fastapi import FastAPI

from app.api.v1 import health, moderation

def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Moderation Platform",
        description="AI-powered content moderation service",
        version="1.0.0"
    )

    app.include_router(
        moderation.router,
        prefix="/api/v1/moderate",
        tags=["moderation"]
    )

    app.include_router(
        health.router,
        prefix="/api/v1/health",
        tags=["health"]
    )
    
    @app.get("/")
    def read_root():
        return {"message": "AI Moderation Platform is running!"}
    
    return app

app = create_app()
