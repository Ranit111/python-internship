"""
Application configuration and security settings.
"""

import os
from typing import List


class Settings:
    PROJECT_NAME: str = "Enterprise Task & Asset Microservice API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "dev-insecure-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours

    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./app.db")
    ALLOWED_ORIGINS: List[str] = ["*"]


settings = Settings()
