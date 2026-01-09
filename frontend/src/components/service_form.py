"""Service form component for creating and editing services.

Provides a form for creating new Azure service definitions.
"""

from typing import Callable

import streamlit as st

from src.api_client import ServiceData


def display_create_service_form(
    on_submit: Callable[[ServiceData], bool],
    categories: list[str] | None = None,
) -> None:
    """Display a form for creating a new service.

    Args:
        on_submit: Callback function to handle form submission.
                  Returns True if successful, False otherwise.
        categories: Optional list of existing categories for suggestions.
    """
    st.subheader("➕ Add New Service")

    with st.form("create_service_form", clear_on_submit=True):
        # Service name input
        service_name = st.text_input(
            "Service Name",
            placeholder="e.g., Azure Container Apps",
            help="Enter the name of the Azure service",
        )

        # Category input with suggestions
        if categories:
            # Show existing categories as suggestions
            col1, col2 = st.columns([3, 1])
            with col1:
                category = st.text_input(
                    "Category",
                    placeholder="e.g., Containers",
                    help="Enter the service category",
                )
            with col2:
                st.markdown("**Suggestions:**")
                st.caption(", ".join(categories[:5]))
        else:
            category = st.text_input(
                "Category",
                placeholder="e.g., Containers",
                help="Enter the service category",
            )

        # Description input
        description = st.text_area(
            "Description",
            placeholder="Enter a detailed description of the service...",
            help="Describe what the service does and its key features",
            height=100,
        )

        # Submit button
        submitted = st.form_submit_button(
            "Create Service",
            use_container_width=True,
            type="primary",
        )

        if submitted:
            # Validate inputs
            if not service_name or not service_name.strip():
                st.error("⚠️ Service name is required.")
                return

            if not category or not category.strip():
                st.error("⚠️ Category is required.")
                return

            if not description or not description.strip():
                st.error("⚠️ Description is required.")
                return

            # Create service data
            new_service = ServiceData(
                service=service_name.strip(),
                category=category.strip(),
                description=description.strip(),
            )

            # Call the submission handler
            success = on_submit(new_service)

            if success:
                st.success(f"✅ Service '{service_name}' created successfully!")
                st.rerun()


def display_service_form_modal(
    on_submit: Callable[[ServiceData], bool],
    categories: list[str] | None = None,
) -> None:
    """Display service form in a modal/expander.

    Args:
        on_submit: Callback function to handle form submission.
        categories: Optional list of existing categories.
    """
    with st.expander("➕ Add New Service", expanded=False):
        display_create_service_form(on_submit, categories)
