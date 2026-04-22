from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve .env relative to this file (backend/app/config.py → backend/.env)
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./test.db"
    secret_key: str = "dev-secret-key-change-in-production"
    resend_api_key: str = ""
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    microsoft_oauth_client_id: str = ""
    microsoft_oauth_client_secret: str = ""
    frontend_url: str = "http://localhost:3000"
    voyage_api_key: str = ""
    claude_api_key: str | None = None
    r2_endpoint_url: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    cookie_secure: bool = False

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8"}


settings = Settings()
