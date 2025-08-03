from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # API Configuration
    api_v1_prefix: str = Field("/api/v1", env = "API_V1_PREFIX")
    
    # Database
    postgres_dsn: str = Field("postgresql://practice@localhost/practice", env = "POSTGRES_DSN")
    
    # Redis
    redis_url: str =  Field("redis://localhost:6379/0", env = "REDIS_URL")
    
    # External APIs
    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(True, env="DEBUG")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )


@lru_cache()
def get_settings():
    return Settings()
