import secrets
from typing import Optional
from pydantic import HttpUrl
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    ENVIRONMENT: str = 'development'
    DATABASE_URL: str
    API_PREFIX: str = "/api/"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None
    APP_HOST: str
    APP_PORT: int
    JSON_LOGS: bool
    GUNICORN_WORKERS: int
    MAIL_PASSWORD: str
    MAIL_SERVER: str
    MAIL_USER: str
    IMAP_PORT: int
    ATTACHMENTS_DIR: str

    class Config:
        env_file = ".env"
        case_sensitive = True


config = Config()

