"""Pytest configuration and fixtures for frontend tests."""

import pytest

from src.api_client import APIClient, ServiceData


@pytest.fixture
def sample_service() -> ServiceData:
    """Sample service data for testing."""
    return ServiceData(
        service="Azure Virtual Machines",
        category="Compute",
        description="On-demand, scalable virtual machines.",
    )


@pytest.fixture
def sample_services() -> list[ServiceData]:
    """Sample list of services for testing."""
    return [
        ServiceData(
            service="Azure Virtual Machines",
            category="Compute",
            description="On-demand, scalable virtual machines.",
        ),
        ServiceData(
            service="Azure App Service",
            category="App Platform",
            description="Fully managed platform for web apps.",
        ),
        ServiceData(
            service="Azure SQL Database",
            category="Databases",
            description="Managed relational database service.",
        ),
    ]
