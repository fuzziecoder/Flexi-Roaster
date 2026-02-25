"""
Configuration settings for FlexiRoaster backend.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Literal, Optional, Union


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

    # Security
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "flexiroaster-api"
    JWT_AUDIENCE: str = "flexiroaster-clients"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # RBAC / API protection
    ENABLE_AUTH: bool = True

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 120

    # Secret manager backend: env|vault
    SECRET_BACKEND: str = "env"

    # Optional enterprise IAM (Keycloak)
    KEYCLOAK_ENABLED: bool = False
    KEYCLOAK_ISSUER: Optional[str] = None
    KEYCLOAK_CLIENT_ID: Optional[str] = None
    # Event-driven architecture (Kafka / Redpanda)
    ENABLE_EVENT_STREAMING: bool = False
    EVENT_STREAM_BACKEND: Literal["kafka", "redpanda"] = "kafka"
    KAFKA_BOOTSTRAP_SERVERS: Union[str, List[str]] = "localhost:9092"
    KAFKA_CLIENT_ID: str = "flexiroaster-backend"

    TOPIC_PIPELINE_CREATED: str = "pipeline.created"
    TOPIC_EXECUTION_STARTED: str = "execution.started"
    TOPIC_EXECUTION_FAILED: str = "execution.failed"
    TOPIC_EXECUTION_COMPLETED: str = "execution.completed"

    # Distributed execution backends: local|celery|ray
    DISTRIBUTED_EXECUTION_BACKEND: str = "local"

    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_EXECUTION_TASK: str = "flexiroaster.execute_pipeline"

    # Ray settings
    RAY_ADDRESS: str = "auto"
    RAY_NAMESPACE: str = "flexiroaster"

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

    # Observability
    ENABLE_PROMETHEUS_METRICS: bool = True
    PIPELINE_SLA_TARGET_SECONDS: float = 30.0

    # Centralized logs (Logstash TCP)
    ENABLE_LOGSTASH_LOGGING: bool = False
    LOGSTASH_HOST: str = "localhost"
    LOGSTASH_PORT: int = 5000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings()
