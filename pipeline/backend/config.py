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
    REDIS_SESSION_TTL: int = 86400  # 24 hours
    REDIS_RATE_LIMIT_WINDOW_SECONDS: int = 60
    REDIS_RATE_LIMIT_MAX_REQUESTS: int = 120

    # Redis queue/broker settings
    REDIS_JOB_QUEUE_KEY: str = "flexiroaster:jobs:default"
    REDIS_JOB_QUEUE_TIMEOUT: int = 5
    
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
    # AI/Model Infrastructure
    # ===================
    FEAST_REPO_PATH: str = "./feature_repo"
    KUBEFLOW_HOST: str = "http://localhost:3000"

    # ===================
    # Logging Settings
    # ===================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"
    LOG_FILE: Optional[str] = None

    # ===================
    # Elasticsearch Settings
    # ===================
    ELASTICSEARCH_ENABLED: bool = True
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_USERNAME: Optional[str] = None
    ELASTICSEARCH_PASSWORD: Optional[str] = None
    ELASTICSEARCH_VERIFY_CERTS: bool = True
    ELASTICSEARCH_LOGS_INDEX: str = "flexiroaster-execution-logs"
    ELASTICSEARCH_REQUEST_TIMEOUT: int = 10
    
    # ===================
    # Observability Settings
    # ===================
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1

    # ===================
    # Airflow Integration
    # ===================
    AIRFLOW_CALLBACK_SECRET: str = ""  # Shared secret for Airflow callbacks

    # ===================
    # Distributed Execution Engine
    # ===================
    EXECUTION_QUEUE_BACKEND: str = "celery"  # celery | inline
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_QUEUE: str = "pipeline_execution"
    CELERY_TASK_NAME: str = "core.tasks.execute_pipeline_task"
    KAFKA_ENABLED: bool = False
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_EXECUTION_TOPIC: str = "pipeline.executions"
    KAFKA_TRIGGER_ENABLED: bool = False
    KAFKA_TRIGGER_TOPIC: str = "pipeline.triggers"
    KAFKA_TRIGGER_GROUP: str = "flexiroaster-orchestrator"

    # Event & messaging provider settings
    EVENT_BACKEND: str = "kafka"  # kafka | pulsar | rabbitmq | nats
    PULSAR_ENABLED: bool = False
    PULSAR_SERVICE_URL: str = "pulsar://localhost:6650"
    PULSAR_EXECUTION_TOPIC: str = "persistent://public/default/pipeline.executions"
    PULSAR_TENANT: str = "public"
    PULSAR_NAMESPACE: str = "default"
    PULSAR_GEO_REPLICATION_REGIONS: List[str] = []

    RABBITMQ_ENABLED: bool = False
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    RABBITMQ_EXCHANGE: str = "pipeline.executions"
    RABBITMQ_QUEUE: str = "pipeline.execution.tasks"

    NATS_ENABLED: bool = False
    NATS_SERVERS: List[str] = ["nats://localhost:4222"]
    NATS_SUBJECT: str = "pipeline.executions"

    # ===================
    # Enterprise Orchestration
    # ===================
    SLA_DEFAULT_STAGE_THRESHOLD_SECONDS: int = 120
    WORKER_AUTOSCALING_MIN: int = 1
    WORKER_AUTOSCALING_MAX: int = 20
    WORKER_AUTOSCALING_SCALE_UP_THRESHOLD: int = 10
    WORKER_AUTOSCALING_SCALE_DOWN_THRESHOLD: int = 2
    WORKER_AUTOSCALING_TARGET_QUEUE_PER_WORKER: int = 3

    # ===================
    # Modern Orchestration Stack
    # ===================
    ORCHESTRATION_ENGINE: str = "temporal"  # temporal | airflow
    TEMPORAL_ENABLED: bool = True
    TEMPORAL_NAMESPACE: str = "default"
    TEMPORAL_TASK_QUEUE: str = "flexiroaster-orchestration"
    TEMPORAL_ADDRESS: str = "localhost:7233"

    KUBERNETES_NAMESPACE: str = "flexiroaster"
    KUBERNETES_JOB_IMAGE: str = "python:3.11-slim"
    KUBERNETES_SERVICE_ACCOUNT: str = "pipeline-runner"

    RAY_ENABLED: bool = True
    RAY_DASHBOARD_URL: str = "http://localhost:8265"
    RAY_JOB_ENTRYPOINT: str = "python -m worker"

    DISTRIBUTED_COMPUTE_BACKEND: str = "ray"  # ray | celery | spark | dask
    SPARK_ENABLED: bool = False
    SPARK_MASTER_URL: str = "spark://localhost:7077"
    SPARK_APP_NAME: str = "flexiroaster-pipeline"
    SPARK_STREAMING_ENABLED: bool = True

    DASK_ENABLED: bool = False
    DASK_SCHEDULER_ADDRESS: str = "tcp://localhost:8786"
    DASK_DASHBOARD_URL: str = "http://localhost:8787"

    OBJECT_STORAGE_ENABLED: bool = True
    OBJECT_STORAGE_BUCKET: str = "pipeline-artifacts"
    OBJECT_STORAGE_ENDPOINT: str = "http://localhost:9000"
    OBJECT_STORAGE_ACCESS_KEY: str = "minio"
    OBJECT_STORAGE_SECRET_KEY: str = "minio123"

    DATABASE_BACKEND: str = "postgresql"  # postgresql | cockroachdb | mongodb | cassandra
    COCKROACHDB_URL: str = "postgresql://root@localhost:26257/flexiroaster?sslmode=disable"
    MONGODB_URL: str = "mongodb://localhost:27017/flexiroaster"
    CASSANDRA_CONTACT_POINTS: List[str] = ["localhost"]
    CASSANDRA_KEYSPACE: str = "flexiroaster"

    JWT_SECRET: str = ""
    JWT_ISSUER: str = "flexiroaster"
    JWT_AUDIENCE: str = "flexiroaster-api"

    SECRETS_PROVIDER: str = "env"  # env | aws | vault
    
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
