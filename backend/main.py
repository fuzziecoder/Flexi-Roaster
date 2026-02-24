"""
FlexiRoaster FastAPI Application.
Main entry point for the REST API server.
"""
from datetime import datetime

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.middleware.rate_limit_middleware import RateLimitMiddleware
from backend.api.routes import airflow, executions, metrics, pipelines
from backend.api.routes.auth import router as auth_router
from backend.api.security import require_roles
from backend.config import settings
from backend.services.secrets import secret_manager

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade pipeline automation backend with AI-powered insights",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

# Request/Response logging middleware
if settings.LOG_REQUESTS:
    from backend.api.middleware.logging_middleware import RequestLoggingMiddleware

    app.add_middleware(RequestLoggingMiddleware)


@app.on_event("startup")
async def load_runtime_secrets() -> None:
    """Load secrets from configured provider when available."""
    jwt_secret = secret_manager.get("JWT_SECRET_KEY")
    if jwt_secret:
        settings.JWT_SECRET_KEY = jwt_secret


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat(),
        },
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_PREFIX}/docs",
        "health": "/health",
    }


# Include routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(
    pipelines.router,
    prefix=settings.API_PREFIX,
    dependencies=[Depends(require_roles("admin", "operator", "viewer"))],
)
app.include_router(
    executions.router,
    prefix=settings.API_PREFIX,
    dependencies=[Depends(require_roles("admin", "operator", "viewer"))],
)
app.include_router(
    metrics.router,
    prefix=settings.API_PREFIX,
    dependencies=[Depends(require_roles("admin", "operator", "viewer"))],
)
app.include_router(
    airflow.router,
    prefix=settings.API_PREFIX,
    dependencies=[Depends(require_roles("admin", "operator"))],
)


# Run server
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
