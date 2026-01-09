"""Streamlit main application for Azure Service Catalog.

Provides a web interface for viewing, creating, updating, and deleting
Azure service definitions.
"""

import logging

import streamlit as st

from src.api_client import APIClient, APIError, ServiceData
from src.components.filters import display_filters, get_unique_categories
from src.components.service_form import display_service_form_modal
from src.components.service_list import display_service_list
from src.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    # Display service list
    display_service_list(services)

    # Footer
    st.markdown("---")
    st.caption("Azure Service Catalog v1.0.0")


if __name__ == "__main__":
    main()
