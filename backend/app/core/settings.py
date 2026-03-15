from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Interactive Cinematic Story Engine API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_allow_origins: str = "*"
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = "gemini-2.5-flash"
    imagen_model: str = "imagen-4.0-generate-001"
    gcs_bucket_name: str = Field(default="", alias="GCS_BUCKET_NAME")
    firebase_project_id: str = Field(default="", alias="FIREBASE_PROJECT_ID")
    firebase_themes_collection: str = Field(default="story_themes", alias="FIREBASE_THEMES_COLLECTION")
    scene_word_limit: int = 120

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
