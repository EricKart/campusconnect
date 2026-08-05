"""
All config comes from environment variables -- never hardcoded. Locally,
docker compose injects these; in Azure, from Day 16, the same variable names
are wired from Key Vault, so app code never changes between environments.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://campusconnect:campusconnect_dev_password@localhost:5432/campusconnect"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
