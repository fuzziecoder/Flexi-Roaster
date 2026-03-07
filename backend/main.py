"""
FlexiRoaster FastAPI Application.
Main entry point for the REST API server.
"""
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime
import uvicorn

from backend.config import settings
from backend.api.routes import pipelines, executions, metrics, airflow, governance, model_serving, orchestration
from backend.api.middleware.gateway_middleware import GatewayMiddleware
from backend.api.security import get_current_auth_context
from backend.api.routes import pipelines, executions, metrics, airflow, observability
from backend.api.routes import pipelines, executions, metrics, airflow, governance
from backend.api.middleware.gateway_middleware import GatewayMiddleware
from backend.api.security import get_current_auth_context
from backend.api.routes import pipelines, executions, metrics, airflow, model_serving, data_platform, ai

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade pipeline automation backend with AI-powered insights",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API gateway middleware
app.add_middleware(GatewayMiddleware)

# Request/Response logging middleware
if settings.LOG_REQUESTS:
    from backend.api.middleware.logging_middleware import RequestLoggingMiddleware
    app.add_middleware(RequestLoggingMiddleware)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat()
    }


# Prometheus Metrics scraping endpoint
@app.get("/metrics", tags=["monitoring"])
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_PREFIX}/docs",
        "health": "/health"
    }


# Include routers
auth_dependencies = [Depends(get_current_auth_context)] if settings.AUTH_ENABLED else []

app.include_router(pipelines.router, prefix=settings.API_PREFIX, dependencies=auth_dependencies)
app.include_router(executions.router, prefix=settings.API_PREFIX, dependencies=auth_dependencies)
app.include_router(metrics.router, prefix=settings.API_PREFIX, dependencies=auth_dependencies)
app.include_router(airflow.router, prefix=settings.API_PREFIX, dependencies=auth_dependencies)
app.include_router(governance.router, prefix=settings.API_PREFIX, dependencies=auth_dependencies)
app.include_router(pipelines.router, prefix=settings.API_PREFIX)
app.include_router(executions.router, prefix=settings.API_PREFIX)
app.include_router(metrics.router, prefix=settings.API_PREFIX)
app.include_router(airflow.router, prefix=settings.API_PREFIX)
app.include_router(observability.router, prefix=settings.API_PREFIX)
app.include_router(model_serving.router, prefix=settings.API_PREFIX)
app.include_router(orchestration.router, prefix=settings.API_PREFIX)
app.include_router(data_platform.router, prefix=settings.API_PREFIX)
app.include_router(ai.router, prefix=settings.API_PREFIX)


# Run server
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
