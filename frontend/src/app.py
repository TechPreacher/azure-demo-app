"""Streamlit main application for Azure Service Catalog.

Provides a web interface for viewing, creating, updating, and deleting
Azure service definitions with Application Insights integration.
"""

import logging

import streamlit as st

from src.api_client import APIClient, APIError, ServiceData
from src.components.filters import display_filters, get_unique_categories
from src.components.service_form import (
    display_edit_service_form,
    display_service_form_modal,
)
from src.components.service_list import display_delete_confirmation, display_service_cards
from src.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Application Insights if connection string is provided
if config.APPLICATIONINSIGHTS_CONNECTION_STRING:
    try:
        from opencensus.ext.azure.log_exporter import AzureLogHandler

        # Add Azure Log Handler for sending logs to App Insights
        azure_handler = AzureLogHandler(
            connection_string=config.APPLICATIONINSIGHTS_CONNECTION_STRING
        )
        logger.addHandler(azure_handler)
        logger.info("Application Insights integration enabled for frontend")
    except ImportError:
        logger.warning(
            "opencensus-ext-azure not installed, Application Insights disabled"
        )
    except Exception as e:
        logger.warning(f"Failed to configure Application Insights: {e}")

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client instance.

    Returns:
        APIClient configured with API base URL.
    """
    return APIClient(base_url=config.API_BASE_URL)


def check_api_health() -> tuple[bool, str]:
    """Check API health status.

    Returns:
        Tuple of (is_healthy, status_message).
    """
    try:
        client = get_api_client()
        health = client.health_check()
        return True, f"✅ {health.get('status', 'healthy').capitalize()}"
    except APIError as e:
        logger.error(f"Health check failed: {e}")
        return False, f"❌ Unavailable: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in health check: {e}")
        return False, f"❌ Error: {e}"


def load_services(
    category: str | None = None,
    search: str | None = None,
) -> tuple[list, str | None]:
    """Load services from the API.

    Args:
        category: Optional category filter.
        search: Optional search term.

    Returns:
        Tuple of (services_list, error_message).
    """
    try:
        client = get_api_client()
        services = client.get_services(category=category, search=search)
        return services, None
    except APIError as e:
        logger.error(f"Failed to load services: {e}")
        return [], f"Failed to load services: {e}"
    except Exception as e:
        logger.error(f"Unexpected error loading services: {e}")
        return [], f"An unexpected error occurred: {e}"


def load_all_categories() -> list[str]:
    """Load all unique categories from the API.

    Returns:
        List of unique category names.
    """
    try:
        client = get_api_client()
        services = client.get_services()
        return get_unique_categories(services)
    except Exception as e:
        logger.error(f"Failed to load categories: {e}")
        return []


def create_service(service: ServiceData) -> bool:
    """Create a new service via the API.

    Args:
        service: Service data to create.

    Returns:
        True if successful, False otherwise.
    """
    try:
        client = get_api_client()
        client.create_service(service)
        logger.info(f"Created service: {service.service}")
        return True
    except APIError as e:
        logger.error(f"Failed to create service: {e}")
        if e.status_code == 409:
            st.error(f"⚠️ A service with name '{service.service}' already exists.")
        else:
            st.error(f"⚠️ Failed to create service: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating service: {e}")
        st.error(f"⚠️ An unexpected error occurred: {e}")
        return False


def update_service(service_name: str, updates: dict[str, str]) -> bool:
    """Update an existing service via the API.

    Args:
        service_name: Name of the service to update.
        updates: Dictionary of fields to update.

    Returns:
        True if successful, False otherwise.
    """
    try:
        client = get_api_client()
        client.update_service(service_name, updates)
        logger.info(f"Updated service: {service_name}")
        return True
    except APIError as e:
        logger.error(f"Failed to update service: {e}")
        if e.status_code == 404:
            st.error(f"⚠️ Service '{service_name}' not found.")
        elif e.status_code == 409:
            st.error(f"⚠️ A service with the new name already exists.")
        else:
            st.error(f"⚠️ Failed to update service: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error updating service: {e}")
        st.error(f"⚠️ An unexpected error occurred: {e}")
        return False


def set_editing_service(service: ServiceData) -> None:
    """Set the service to edit in session state.

    Args:
        service: Service to edit.
    """
    st.session_state["editing_service"] = service


def clear_editing_service() -> None:
    """Clear the editing service from session state."""
    if "editing_service" in st.session_state:
        del st.session_state["editing_service"]


def delete_service(service_name: str) -> bool:
    """Delete a service via the API.

    Args:
        service_name: Name of the service to delete.

    Returns:
        True if successful, False otherwise.
    """
    try:
        client = get_api_client()
        client.delete_service(service_name)
        logger.info(f"Deleted service: {service_name}")
        return True
    except APIError as e:
        logger.error(f"Failed to delete service: {e}")
        if e.status_code == 404:
            st.error(f"⚠️ Service '{service_name}' not found.")
        else:
            st.error(f"⚠️ Failed to delete service: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting service: {e}")
        st.error(f"⚠️ An unexpected error occurred: {e}")
        return False


def set_deleting_service(service: ServiceData) -> None:
    """Set the service to delete in session state.

    Args:
        service: Service to delete.
    """
    st.session_state["deleting_service"] = service


def clear_deleting_service() -> None:
    """Clear the deleting service from session state."""
    if "deleting_service" in st.session_state:
        del st.session_state["deleting_service"]


def main() -> None:
    """Main application entry point."""
    # Header
    st.title(f"{config.PAGE_ICON} Azure Service Catalog")
    st.markdown("Browse, search, and manage Azure service definitions.")

    # Sidebar
    with st.sidebar:
        st.markdown(f"**API URL:** `{config.API_BASE_URL}`")

        # Health check status
        st.markdown("---")
        st.subheader("System Status")
        is_healthy, status_msg = check_api_health()
        st.markdown(status_msg)

        if not is_healthy:
            st.warning(
                "The API is currently unavailable. "
                "Please ensure the backend service is running."
            )
            st.stop()

        st.markdown("---")

        # Load categories for filter dropdown
        categories = load_all_categories()

        # Display filters in sidebar
        selected_category, search_term = display_filters(categories=categories)

    # Main content area
    st.markdown("---")

    # Check if we're editing a service
    editing_service = st.session_state.get("editing_service")
    deleting_service = st.session_state.get("deleting_service")

    if deleting_service:
        # Display delete confirmation
        display_delete_confirmation(
            service=deleting_service,
            on_confirm=delete_service,
            on_cancel=clear_deleting_service,
        )
    elif editing_service:
        # Display edit form
        display_edit_service_form(
            service=editing_service,
            on_submit=update_service,
            on_cancel=clear_editing_service,
            categories=categories,
        )
    else:
        # Add new service form (collapsible)
        display_service_form_modal(on_submit=create_service, categories=categories)

    st.markdown("---")

    # Load services with filters
    with st.spinner("Loading services..."):
        services, error = load_services(
            category=selected_category,
            search=search_term,
        )

    # Display error if any
    if error:
        st.error(error)
        st.stop()

    # Display service list with edit and delete capability
    display_service_cards(
        services,
        on_edit=set_editing_service,
        on_delete=set_deleting_service,
    )

    # Footer
    st.markdown("---")
    st.caption("Azure Service Catalog v1.0.0")


if __name__ == "__main__":
    main()
