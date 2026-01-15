"""
FlexiRoaster Pipeline Automation Configuration.
Centralized configuration management using environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # ===================
    # Application Settings
    # ===================
    APP_NAME: str = "FlexiRoaster"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # ===================
    # API Settings
    # ===================
    API_PREFIX: str = "/api"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    # ===================
    # Server Settings
    # ===================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # ===================
    # Database Settings
    # ===================
    DATABASE_URL: str = "postgresql+psycopg2://airflow:airflow@localhost:5432/flexiroaster"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False
    
    # ===================
    # Redis Settings
    # ===================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_EXECUTION_DB: int = 1
    REDIS_CACHE_DB: int = 2
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: float = 5.0
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_DECODE_RESPONSES: bool = True
    
    # Execution Lock Settings
    EXECUTION_LOCK_TTL: int = 3600  # 1 hour
    EXECUTION_LOCK_RETRY_DELAY: float = 0.5
    EXECUTION_LOCK_MAX_RETRIES: int = 10
    
    # Heartbeat Settings
    HEARTBEAT_INTERVAL: int = 30  # seconds
    HEARTBEAT_TTL: int = 90  # 3x interval
    
    # ===================
    # Executor Settings
    # ===================
    EXECUTOR_DEFAULT_TIMEOUT: int = 300  # 5 minutes
    EXECUTOR_STAGE_TIMEOUT: int = 120  # 2 minutes per stage
    EXECUTOR_MAX_RETRIES: int = 3
    EXECUTOR_RETRY_DELAY: float = 1.0
    EXECUTOR_RETRY_BACKOFF: float = 2.0
    
    # ===================
    # AI Safety Settings
    # ===================
    AI_RISK_THRESHOLD_HIGH: float = 0.7
    AI_RISK_THRESHOLD_MEDIUM: float = 0.4
    AI_RISK_THRESHOLD_LOW: float = 0.2
    AI_BLOCK_HIGH_RISK: bool = False  # If True, block high-risk executions
    AI_ANOMALY_DETECTION_ENABLED: bool = True
    AI_ANOMALY_TIME_MULTIPLIER: float = 3.0  # Times avg duration = anomaly
    AI_ANOMALY_ERROR_THRESHOLD: int = 5  # Errors before anomaly
    
    # ===================
    # Logging Settings
    # ===================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"
    LOG_FILE: Optional[str] = None
    
    # ===================
    # Airflow Integration
    # ===================
    AIRFLOW_CALLBACK_SECRET: str = ""  # Shared secret for Airflow callbacks
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
