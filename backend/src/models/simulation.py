"""Simulation response models for telemetry testing endpoints.

Provides Pydantic models for latency and error simulation responses.
"""

from pydantic import BaseModel, Field


class LatencySimulationResponse(BaseModel):
    """Response model for latency simulation endpoint.

    Attributes:
        status: Operation status, always "completed" on success.
        delay_seconds: Actual delay applied in seconds (10.0-20.0 range).
        message: Human-readable completion message.
    """

    status: str = Field(default="completed", description="Operation status")
    delay_seconds: float = Field(
        ge=10.0, le=20.0, description="Applied delay in seconds"
    )
    message: str = Field(
        default="Latency simulation completed successfully",
        description="Human-readable completion message",
    )
