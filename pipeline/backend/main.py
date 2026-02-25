"""
FlexiRoaster Pipeline Automation - FastAPI Application.
Production-ready REST API for pipeline orchestration.
"""
import logging
import asyncio
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import structlog

from config import settings
from db import create_tables
from core.redis_state import redis_state_manager
from core.executor import pipeline_executor
from api.routes import ai_automation, executions, health, microservices, model_infra, monitoring, orchestration, pipelines
from api.routes import (
    advanced_stack,
    ai_automation,
    executions,
    health,
    microservices,
    model_infra,
    monitoring,
    pipelines,
)
from core.elasticsearch_client import elasticsearch_manager
from observability import setup_observability
from core.enterprise_orchestration import DynamicDAGGenerator, KafkaExecutionTrigger
from db import get_db, PipelineCRUD


# ===================
# Logging Setup
# ===================

def setup_logging():
    """Configure structured logging"""
    if settings.LOG_FORMAT == "json":
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        stream=sys.stdout
    )


setup_logging()
logger = logging.getLogger(__name__)

kafka_trigger = KafkaExecutionTrigger()


async def _handle_kafka_trigger_event(event: dict):
    """Handle Kafka event and execute generated or stored pipeline."""
    pipeline_id = event.get("pipeline_id", "event-driven")
    pipeline_name = event.get("pipeline_name", pipeline_id)
    metadata = event.get("metadata")

    if metadata:
        spec = DynamicDAGGenerator().generate(metadata)
        stages = spec.stages
    else:
        with get_db() as db:
            pipeline = PipelineCRUD.get_by_id(db, pipeline_id)
            if not pipeline or not pipeline.is_active:
                logger.warning("Ignoring Kafka trigger for unknown/inactive pipeline", extra={"pipeline_id": pipeline_id})
                return
            pipeline_name = pipeline.name
            stages = [
                {
                    "id": s.stage_id,
                    "name": s.name,
                    "type": s.stage_type,
                    "config": s.config or {},
                    "dependencies": s.dependencies or [],
                    "timeout": s.timeout,
                    "max_retries": s.max_retries,
                    "retry_delay": s.retry_delay,
                    "is_critical": s.is_critical,
                }
                for s in pipeline.stages
            ]

    await pipeline_executor.execute_pipeline(
        pipeline_id=pipeline_id,
        pipeline_name=pipeline_name,
        stages=stages,
        variables=event.get("variables", {}),
        triggered_by="kafka",
        trigger_metadata={"event": event},
    )




# ===================
# Application Lifecycle
# ===================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Create database tables
    create_tables()
    logger.info("Database tables initialized")
    
    # Initialize Redis
    await redis_state_manager.initialize()
    logger.info("Redis state manager initialized")
    
    # Initialize executor
    await pipeline_executor.initialize()
    logger.info("Pipeline executor initialized")

    # Initialize Elasticsearch
    await elasticsearch_manager.initialize()
    logger.info("Elasticsearch manager initialized")
    
    kafka_task = None
    if settings.KAFKA_TRIGGER_ENABLED:
        kafka_task = asyncio.create_task(kafka_trigger.consume(_handle_kafka_trigger_event))

    logger.info(f"Application ready on {settings.HOST}:{settings.PORT}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    kafka_trigger.stop()
    if kafka_task:
        await kafka_task
    await pipeline_executor.shutdown()
    await redis_state_manager.close()
    await elasticsearch_manager.close()
    logger.info("Application shutdown complete")


# ===================
# Create FastAPI App
# ===================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    FlexiRoaster Pipeline Automation System
    
    A production-ready pipeline orchestration system with:
    - RESTful API for pipeline management
    - AI-powered failure prediction
    - Redis-based state management
    - Distributed execution locking
    - Real-time execution monitoring
    
    ## Features
    - Create, update, and manage data pipelines
    - Execute pipelines with automatic retries
    - Monitor execution status in real-time
    - AI safety checks before and during execution
    - Comprehensive logging and metrics
    
    ## Integration
    - Works with Apache Airflow for scheduling
    - Redis for distributed state
    - PostgreSQL for persistence
    """,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan
)


# ===================
# Middleware
# ===================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure metrics and error monitoring
setup_observability(app)


# ===================
# Exception Handlers
# ===================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# ===================
# Root Endpoints
# ===================

@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Pipeline Automation System",
        "docs": f"{settings.API_PREFIX}/docs",
        "health": "/health",
        "api_prefix": settings.API_PREFIX
    }


# ===================
# Include Routers
# ===================

# Health routes at root level
app.include_router(health.router)

# API routes with prefix
app.include_router(pipelines.router, prefix=settings.API_PREFIX)
app.include_router(executions.router, prefix=settings.API_PREFIX)
app.include_router(monitoring.router, prefix=settings.API_PREFIX)
app.include_router(ai_automation.router, prefix=settings.API_PREFIX)
app.include_router(microservices.router, prefix=settings.API_PREFIX)
app.include_router(model_infra.router, prefix=settings.API_PREFIX)
app.include_router(orchestration.router, prefix=settings.API_PREFIX)
app.include_router(advanced_stack.router, prefix=settings.API_PREFIX)


# ===================
# Airflow Callback Endpoint
# ===================

@app.post(f"{settings.API_PREFIX}/airflow/callback", tags=["airflow"])
async def airflow_callback(request: Request):
    """
    Callback endpoint for Airflow DAGs.
    Receives notifications about DAG run status.
    """
    try:
        data = await request.json()
        
        # Validate callback secret if configured
        if settings.AIRFLOW_CALLBACK_SECRET:
            auth_header = request.headers.get("X-Airflow-Secret", "")
            if auth_header != settings.AIRFLOW_CALLBACK_SECRET:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid callback secret"}
                )
        
        logger.info(f"Airflow callback received: {data}")
        
        # Process callback based on type
        callback_type = data.get("callback_type", "unknown")
        dag_id = data.get("dag_id")
        dag_run_id = data.get("dag_run_id")
        
        if callback_type == "success":
            logger.info(f"DAG {dag_id} run {dag_run_id} completed successfully")
        elif callback_type == "failure":
            logger.warning(f"DAG {dag_id} run {dag_run_id} failed")
        elif callback_type == "retry":
            logger.info(f"DAG {dag_id} run {dag_run_id} retrying")
        
        return {
            "success": True,
            "message": f"Callback processed: {callback_type}",
            "dag_id": dag_id,
            "dag_run_id": dag_run_id
        }
        
    except Exception as e:
        logger.error(f"Airflow callback error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# ===================
# Run Server
# ===================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
