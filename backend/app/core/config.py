"""
Application configuration.
Values are loaded from environment variables / .env file.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # General
    APP_NAME: str = "AI Product Inspection System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://inspection_user:inspection_pass@localhost:5432/inspection_db"

    # Security
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    # File storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 15

    # AI Models
    MODEL_DIR: str = "ai_models/weights"
    PRODUCT_DETECTION_MODEL: str = "product_detector.pt"
    COMPONENT_DETECTION_MODEL: str = "component_detector.pt"
    DEFECT_DETECTION_MODEL: str = "defect_detector.pt"
    CONFIDENCE_THRESHOLD: float = 0.5

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
