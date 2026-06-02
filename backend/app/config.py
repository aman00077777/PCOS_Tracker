import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # JWT Config
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkeyforpcostrackingapp12345!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    # Standard SQLite default if PostgreSQL not configured
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pcos_tracker.db")

    # OAuth Google (placeholder settings to support architecture)
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501/auth/callback")

    # Discord Reminders
    DISCORD_WEBHOOK_URL: Optional[str] = os.getenv("DISCORD_WEBHOOK_URL", None)

    # Email Reminders (SMTP)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER", None)
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD", None)
    MAIL_FROM: str = os.getenv("MAIL_FROM", "reminders@pcostracker.org")

    # ML Model Config
    MODEL_PATH: str = os.getenv("MODEL_PATH", "ml/models/pcos_rf_model.pkl")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
