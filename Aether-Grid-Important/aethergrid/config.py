import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """System-wide configuration for AetherGrid."""
    APP_NAME: str = "AetherGrid"
    DEBUG: bool = False
    
    # Leader configuration
    LEADER_HOST: str = "0.0.0.0"
    LEADER_PORT: int = 8000
    LEADER_URL: str = f"http://127.0.0.1:{LEADER_PORT}"
    
    # Database configuration
    DB_PATH: str = "aethergrid.db"
    DB_FLUSH_INTERVAL: int = 10  # seconds
    
    # Worker configuration
    NUM_WORKERS: int = 4
    WORKER_POLL_INTERVAL: float = 1.5
    WORKER_TIMEOUT: float = 10.0

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
