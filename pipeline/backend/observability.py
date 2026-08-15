"""Observability setup for metrics and error monitoring."""
import logging

import sentry_sdk
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from config import settings

logger = logging.getLogger(__name__)


def setup_observability(app: FastAPI) -> None:
    """Configure Prometheus metrics and Sentry error monitoring."""
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=False,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="flexiroaster_inprogress",
        inprogress_labels=True,
    ).instrument(app).expose(app, include_in_schema=False)

    if not settings.SENTRY_DSN:
        logger.info("Sentry disabled - SENTRY_DSN not configured")
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        release=f"{settings.APP_NAME}@{settings.APP_VERSION}",
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
    )
    app.add_middleware(SentryAsgiMiddleware)
    logger.info("Sentry error monitoring enabled")
