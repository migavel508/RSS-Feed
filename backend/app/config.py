from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from typing import Optional
import json
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    FEED_CONFIG_PATH: str = "feeds_config.json"
    FETCH_INTERVAL: int = 30  # minutes
    
    # Neo4j settings
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    class Config:
        env_file = ".env"

settings = Settings()

def load_feed_config() -> dict:
    config_path = Path(settings.FEED_CONFIG_PATH)
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {} 