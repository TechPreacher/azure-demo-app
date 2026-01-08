"""Pydantic models for Azure services."""

from pydantic import BaseModel, Field


class ServiceBase(BaseModel):
    """Base model for Azure service data."""

    service: str = Field(
        ...,
        description="Name of the Azure service",
        examples=["Azure Virtual Machines"],
    )
    category: str = Field(
        ...,
        description="Category of the service",
        examples=["Compute", "Storage", "Databases"],
    )
    description: str = Field(
        ...,
        description="Detailed description of the service",
        examples=["On-demand, scalable virtual machines for Windows and Linux workloads."],
    )


class ServiceCreate(ServiceBase):
    """Model for creating a new service."""

    pass


class ServiceUpdate(BaseModel):
    """Model for updating an existing service.

    All fields are optional to allow partial updates.
    """

    service: str | None = Field(
        default=None,
        description="New name for the service",
    )
    category: str | None = Field(
        default=None,
        description="New category for the service",
    )
    description: str | None = Field(
        default=None,
        description="New description for the service",
    )


class Service(ServiceBase):
    """Complete service model returned from API."""

    model_config = {"from_attributes": True}


class ServiceList(BaseModel):
    """Response model for list of services."""

    services: list[Service] = Field(
        default_factory=list,
        description="List of Azure services",
    )
    total: int = Field(
        ...,
        description="Total number of services",
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str = Field(
        ...,
        description="Error message",
    )
    error_code: str | None = Field(
        default=None,
        description="Application-specific error code",
    )
