from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Moderation Platform",
        description="AI-powered content moderation service",
        version="1.0.0"
    )
    
    @app.get("/")
    def read_root():
        return {"message": "AI Moderation Platform is running!"}
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy"}
    
    
    return app

app = create_app()
