"""FastAPI application entry point.

Provides the main FastAPI app with CORS, health endpoint,
structured logging, Application Insights integration, and API routes.
"""

import logging
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router
from src.config import get_settings

# Configure structured JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Configure Application Insights if connection string is provided
settings = get_settings()
if settings.applicationinsights_connection_string:
    try:
        from opencensus.ext.azure.log_exporter import AzureLogHandler
        from opencensus.ext.azure.trace_exporter import AzureExporter
        from opencensus.trace.samplers import ProbabilitySampler
        from opencensus.trace.tracer import Tracer

        # Add Azure Log Handler for sending logs to App Insights
        azure_handler = AzureLogHandler(
            connection_string=settings.applicationinsights_connection_string
        )
        logger.addHandler(azure_handler)

        # Configure trace exporter for distributed tracing
        exporter = AzureExporter(
            connection_string=settings.applicationinsights_connection_string
        )
        tracer = Tracer(exporter=exporter, sampler=ProbabilitySampler(1.0))

        logger.info("Application Insights integration enabled")
    except ImportError:
        logger.warning(
            "opencensus-ext-azure not installed, Application Insights disabled"
        )
    except Exception as e:
        logger.warning(f"Failed to configure Application Insights: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    settings = get_settings()
    logger.info(
        f"Starting Azure Service Catalog API "
        f"(storage_type={settings.storage_type}, debug={settings.debug})"
    )
    yield
    logger.info("Shutting down Azure Service Catalog API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="Azure Service Catalog API",
        description="RESTful API for managing Azure service definitions",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add correlation ID middleware
    @app.middleware("http")
    async def add_correlation_id(request: Request, call_next) -> Response:
        """Add correlation ID to request for distributed tracing."""
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next) -> Response:
        """Log all incoming requests."""
        start_time = datetime.now(timezone.utc)
        correlation_id = getattr(request.state, "correlation_id", "unknown")

        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"correlation_id={correlation_id}"
        )

        response = await call_next(request)

        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"status={response.status_code} duration_ms={duration_ms:.2f} "
            f"correlation_id={correlation_id}"
        )

        return response

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, Any]:
        """Health check endpoint.

        Returns basic service status for monitoring and load balancers.
        """
        return {
            "status": "healthy",
            "service": "azure-service-catalog-api",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root() -> dict[str, str]:
        """Root endpoint with API information."""
        return {
            "name": "Azure Service Catalog API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }

    # Register API routes
    app.include_router(api_router)

    return app


# Create the application instance
app = create_app()
