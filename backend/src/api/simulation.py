"""Simulation endpoints for telemetry testing.

Provides endpoints to simulate latency and error scenarios for testing
Application Insights traces and exceptions.
"""

import asyncio
import logging
import random
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from src.models.simulation import LatencySimulationResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/simulate", tags=["Simulation"])

# Error message pool for realistic failure simulation
ERROR_MESSAGES: list[str] = [
    "Database connection pool exhausted after 10 retries",
    "Memory allocation failed during request processing",
    "Upstream service 'inventory-api' timed out after 30 seconds",
    "Disk I/O error: Unable to write to temporary storage",
    "SSL certificate validation failed for external dependency",
    "Request payload exceeded maximum allowed size",
    "Rate limit exceeded: Too many requests from client",
    "Cache invalidation cascade triggered system protection",
]


@router.post(
    "/latency",
    response_model=LatencySimulationResponse,
    summary="Simulate high latency response",
    description="Introduces a random delay between 10 and 20 seconds before responding. "
    "Used for testing timeout handling and Application Insights duration tracking.",
)
async def simulate_latency() -> LatencySimulationResponse:
    """Simulate a high-latency backend response.

    Introduces a random delay between 10 and 20 seconds using async sleep,
    which does not block other requests.

    Returns:
        LatencySimulationResponse with actual delay duration.
    """
    delay = random.uniform(10.0, 20.0)
    logger.info(f"Starting latency simulation: {delay:.2f} seconds")

    await asyncio.sleep(delay)

    logger.info(f"Latency simulation completed: {delay:.2f} seconds")
    return LatencySimulationResponse(delay_seconds=round(delay, 2))


@router.post(
    "/error",
    summary="Simulate server error response",
    description="Returns HTTP 500 Internal Server Error with a randomly selected "
    "realistic error message. Used for testing error handling and Application Insights Failures view.",
    responses={
        500: {
            "description": "Simulated internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "message": "Database connection pool exhausted after 10 retries",
                            "error_id": "550e8400-e29b-41d4-a716-446655440000",
                            "timestamp": "2026-01-12T10:30:00Z",
                        }
                    }
                }
            },
        }
    },
)
async def simulate_error() -> None:
    """Simulate a 500 Internal Server Error.

    Selects a random error message from the predefined pool and raises
    an HTTPException with structured error details for Application Insights.

    Raises:
        HTTPException: Always raises 500 with realistic error details.
    """
    error_id = str(uuid.uuid4())
    message = random.choice(ERROR_MESSAGES)
    timestamp = datetime.now(timezone.utc).isoformat()

    logger.error(f"Simulating error: {message} (error_id={error_id})")

    raise HTTPException(
        status_code=500,
        detail={
            "message": message,
            "error_id": error_id,
            "timestamp": timestamp,
        },
    )
