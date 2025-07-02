from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from typing import Optional
import json
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    FEED_CONFIG_PATH: str = "feeds_config.json"
    FETCH_INTERVAL: int = 30  # minutes
    
    class Config:
        env_file = ".env"

settings = Settings()

def load_feed_config() -> dict:
    config_path = Path(settings.FEED_CONFIG_PATH)
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {} 