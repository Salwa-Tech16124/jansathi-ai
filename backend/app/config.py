import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "JanSathi AI"
    VERSION: str = "0.1.0"
    API_PREFIX: str = ""

    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "*"]

    # Database Configuration (SQLite)
    DATABASE_URL: str = "sqlite:///./jansathi.db"

    # Sarvam AI Configuration
    SARVAM_API_KEY: Optional[str] = None
    SARVAM_BASE_URL: str = "https://api.sarvam.ai"
    SARVAM_MODEL: str = "sarvam-2b"

    # Twilio WhatsApp Sandbox Configuration
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
