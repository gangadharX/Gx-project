from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # AI
    GOOGLE_API_KEY: str
    GROQ_API_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # External APIs
    PRODUCTHUNT_TOKEN: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
