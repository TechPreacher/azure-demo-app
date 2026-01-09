"""API routes for Azure Service Catalog.

Provides RESTful endpoints for CRUD operations on Azure services.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from src.api.dependencies import StorageDep
from src.models.service import Service, ServiceList
from src.services.storage import ServiceNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Services"])


@router.get(
    "/services",
    response_model=ServiceList,
    summary="List all services",
    description="Retrieve all Azure services, optionally filtered by category or search term.",
)
async def list_services(
    storage: StorageDep,
    category: Annotated[
        str | None,
        Query(description="Filter by service category (case-insensitive)"),
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Search in service name or description (case-insensitive)"),
    ] = None,
) -> ServiceList:
    """List all Azure services with optional filtering.

    Args:
        storage: Storage adapter dependency.
        category: Optional category filter.
        search: Optional search term.

    Returns:
        ServiceList with matching services and total count.
    """
    logger.info(f"Listing services: category={category}, search={search}")

    services = storage.list_services(category=category, search=search)

    logger.info(f"Found {len(services)} services")
    return ServiceList(services=services, total=len(services))


@router.get(
    "/services/{service_name}",
    response_model=Service,
    summary="Get a service by name",
    description="Retrieve a single Azure service by its exact name.",
    responses={
        404: {
            "description": "Service not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Service not found: Example Service"}
                }
            },
        }
    },
)
async def get_service(
    service_name: str,
    storage: StorageDep,
) -> Service:
    """Get a single Azure service by name.

    Args:
        service_name: Exact name of the service.
        storage: Storage adapter dependency.

    Returns:
        The requested service.

    Raises:
        HTTPException: 404 if service not found.
    """
    logger.info(f"Getting service: {service_name}")

    try:
        service = storage.get_service(service_name)
        return service
    except ServiceNotFoundError as e:
        logger.warning(f"Service not found: {service_name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
