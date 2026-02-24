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

    # API Gateway
    API_GATEWAY_PROVIDER: str = "kong"
    GATEWAY_KEY_HEADER: str = "x-gateway-key"
    TRUSTED_GATEWAY_KEY: Optional[str] = None

    # OAuth2 / OpenID Connect
    AUTH_ENABLED: bool = True
    OIDC_ISSUER_URL: Optional[str] = None
    OIDC_AUDIENCE: Optional[str] = None

    # Data governance
    ATLAS_BASE_URL: Optional[str] = None
    ATLAS_API_TOKEN: Optional[str] = None
    AMUNDSEN_BASE_URL: Optional[str] = None
    AMUNDSEN_API_TOKEN: Optional[str] = None

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from a comma-separated string or return list as-is."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    

    # Model Serving & Deployment
    MODEL_SERVING: str = "FastAPI / Flask (custom APIs), TorchServe / TensorFlow Serving (framework-specific), BentoML (multi-framework)"
    CONTAINERIZATION: str = "Docker"
    ORCHESTRATION: str = "Kubernetes + KServe / Seldon Core"

    # Data platform stack
    DATA_INGESTION: str = "Apache Kafka / Redpanda (streaming), Apache NiFi (ETL)"
    DATA_LAKE: str = "Amazon S3 / Google Cloud Storage / Azure Blob"
    DATA_WAREHOUSE: str = "Snowflake / BigQuery / Amazon Redshift"
    FEATURE_STORE: str = "Feast / Tecton"

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

    # Observability integrations
    GRAFANA_ENABLED: bool = True
    GRAFANA_URL: Optional[str] = None
    ELK_ENABLED: bool = True
    ELK_ENDPOINT: Optional[str] = None

    EVIDENTLY_ENABLED: bool = True
    EVIDENTLY_API_KEY: Optional[str] = None
    ARIZE_ENABLED: bool = True
    ARIZE_SPACE_KEY: Optional[str] = None
    ARIZE_API_KEY: Optional[str] = None
    FIDDLER_ENABLED: bool = True
    FIDDLER_URL: Optional[str] = None
    FIDDLER_API_KEY: Optional[str] = None

    PAGERDUTY_ENABLED: bool = True
    PAGERDUTY_ROUTING_KEY: Optional[str] = None
    OPSGENIE_ENABLED: bool = True
    OPSGENIE_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings()
