"""Application configuration for Nexus Inventory Platform."""

from dataclasses import dataclass
import os


@dataclass
class Settings:
    APP_NAME: str = "Nexus Inventory Platform"
    APP_VERSION: str = "1.4.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///nexus_platform.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "nexus-insecure-dev-key-change-in-prod")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    API_V1_PREFIX: str = "/api/v1"


settings = Settings()
