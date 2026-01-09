"""API routes for Azure Service Catalog.

Provides RESTful endpoints for CRUD operations on Azure services.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from src.api.dependencies import StorageDep
from src.models.service import Service, ServiceCreate, ServiceList, ServiceUpdate
from src.services.storage import DuplicateServiceError, ServiceNotFoundError

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


@router.post(
    "/services",
    response_model=Service,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new service",
    description="Add a new Azure service to the catalog.",
    responses={
        409: {
            "description": "Service already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "Service already exists: Example Service"}
                }
            },
        }
    },
)
async def create_service(
    service: ServiceCreate,
    storage: StorageDep,
) -> Service:
    """Create a new Azure service.

    Args:
        service: Service data to create.
        storage: Storage adapter dependency.

    Returns:
        The created service.

    Raises:
        HTTPException: 409 if service name already exists.
    """
    logger.info(f"Creating service: {service.service}")

    try:
        created = storage.create_service(service)
        logger.info(f"Created service: {created.service}")
        return created
    except DuplicateServiceError as e:
        logger.warning(f"Duplicate service: {service.service}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.put(
    "/services/{service_name}",
    response_model=Service,
    summary="Update an existing service",
    description="Update an existing Azure service. All fields are optional.",
    responses={
        404: {
            "description": "Service not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Service not found: Example Service"}
                }
            },
        },
        409: {
            "description": "Name conflict with existing service",
            "content": {
                "application/json": {
                    "example": {"detail": "Service already exists: Example Service"}
                }
            },
        },
    },
)
async def update_service(
    service_name: str,
    update: ServiceUpdate,
    storage: StorageDep,
) -> Service:
    """Update an existing Azure service.

    Args:
        service_name: Name of the service to update.
        update: Fields to update (partial update supported).
        storage: Storage adapter dependency.

    Returns:
        The updated service.

    Raises:
        HTTPException: 404 if service not found.
        HTTPException: 409 if new name conflicts with existing service.
    """
    logger.info(f"Updating service: {service_name}")

    try:
        updated = storage.update_service(service_name, update)
        logger.info(f"Updated service: {service_name}")
        return updated
    except ServiceNotFoundError as e:
        logger.warning(f"Service not found: {service_name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except DuplicateServiceError as e:
        logger.warning(f"Name conflict updating service: {service_name}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
