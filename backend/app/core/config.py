from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "VRPTW Delivery Planning API"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg://vrptw:vrptw@localhost:5432/vrptw"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 7

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    STORAGE_DIR: str = "storage/runs"

    DEFAULT_SEED: int = 20261022
    DEFAULT_ANOMALY_RATE: float = 0.02


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
