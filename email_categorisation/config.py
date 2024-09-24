import secrets
from typing import List, Optional, Union
from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    ENVIRONMENT: str = 'development'
    DATABASE_URL: str
    API_PREFIX: str = "/api/"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None

    APP_HOST: str
    APP_PORT: int

    JSON_LOGS: bool
    GUNICORN_WORKERS: int

    class Config:
        env_file = ".env"
        case_sensitive = True


config = Config()
