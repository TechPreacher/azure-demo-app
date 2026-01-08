"""Streamlit main application for Azure Service Catalog.

Provides a web interface for viewing, creating, updating, and deleting
Azure service definitions.
"""

import streamlit as st

from src.config import config

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Main application entry point."""
    # Header
    st.title(f"{config.PAGE_ICON} Azure Service Catalog")
    st.markdown("Browse, search, and manage Azure service definitions.")

    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        st.markdown("---")
        st.markdown(f"**API URL:** `{config.API_BASE_URL}`")

        # Health check status
        st.markdown("---")
        st.subheader("System Status")
        # TODO: Add health check display in US1

    # Main content area
    st.markdown("---")

    # Placeholder for service list (US1)
    st.info(
        "🚧 **Coming Soon**\n\n"
        "The service catalog will be displayed here. "
        "This is a skeleton application - implement User Story 1 to add the service list."
    )

    # Footer
    st.markdown("---")
    st.caption("Azure Service Catalog v1.0.0")


if __name__ == "__main__":
    main()
