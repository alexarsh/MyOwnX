"""Runtime configuration, loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret: str
    user_service_url: str
    post_service_url: str


settings = Settings()
