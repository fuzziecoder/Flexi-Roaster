"""
Configuration settings for FlexiRoaster backend.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "FlexiRoaster"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_PREFIX: str = "/api"
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"
    AIRFLOW_CALLBACK_SECRET: Optional[str] = None
    AIRFLOW_TRIGGER_SECRET: Optional[str] = None

    # Event-driven architecture (Kafka)
    ENABLE_EVENT_STREAMING: bool = False
    KAFKA_BOOTSTRAP_SERVERS: Union[str, List[str]] = "localhost:9092"
    KAFKA_CLIENT_ID: str = "flexiroaster-backend"

    TOPIC_PIPELINE_CREATED: str = "pipeline.created"
    TOPIC_EXECUTION_STARTED: str = "execution.started"
    TOPIC_EXECUTION_FAILED: str = "execution.failed"
    TOPIC_EXECUTION_COMPLETED: str = "execution.completed"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from a comma-separated string or return list as-is."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("KAFKA_BOOTSTRAP_SERVERS", mode="before")
    @classmethod
    def parse_kafka_bootstrap_servers(cls, v):
        """Parse KAFKA_BOOTSTRAP_SERVERS from comma-separated values or return list as-is."""
        if isinstance(v, str):
            return [server.strip() for server in v.split(",") if server.strip()]
        return v
    
    # Database
    DATABASE_URL: str = "sqlite:///./flexiroaster.db"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_REQUESTS: bool = True
    LOG_REQUEST_BODY: bool = False
    LOG_RESPONSE_BODY: bool = False
    SENSITIVE_FIELDS: List[str] = ["password", "token", "secret", "api_key", "authorization", "credit_card", "ssn"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings()
