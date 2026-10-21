from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(ROOT_DIR / '.env'), extra='ignore')
    mongodb_url: str
    mongodb_database: str = 'test_students_base'
    jwt_secret: str
    jwt_algorithm: str = 'HS256'
    jwt_expire_minutes: int = 60
    rabbitmq_url: str
    max_retries: int = 3
    processing_delay_seconds: int = 55
    cors_origins: str = 'http://localhost:3000'
    redis_url: str


settings = Settings()
