"""Service form component for creating and editing services.

Provides a form for creating new Azure service definitions
and editing existing services.
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


def display_edit_service_form(
    service: ServiceData,
    on_submit: Callable[[str, dict[str, str]], bool],
    on_cancel: Callable[[], None] | None = None,
    categories: list[str] | None = None,
) -> None:
    """Display a form for editing an existing service.

    Args:
        service: The service to edit.
        on_submit: Callback function to handle form submission.
                  Takes original service name and dict of updates.
                  Returns True if successful, False otherwise.
        on_cancel: Optional callback to handle cancellation.
        categories: Optional list of existing categories for suggestions.
    """
    st.subheader(f"✏️ Edit Service: {service.service}")

    with st.form("edit_service_form"):
        # Service name input (pre-filled)
        service_name = st.text_input(
            "Service Name",
            value=service.service,
            help="Change the name of the Azure service",
        )

        # Category input with suggestions (pre-filled)
        if categories:
            col1, col2 = st.columns([3, 1])
            with col1:
                category = st.text_input(
                    "Category",
                    value=service.category,
                    help="Enter the service category",
                )
            with col2:
                st.markdown("**Suggestions:**")
                st.caption(", ".join(categories[:5]))
        else:
            category = st.text_input(
                "Category",
                value=service.category,
                help="Enter the service category",
            )

        # Description input (pre-filled)
        description = st.text_area(
            "Description",
            value=service.description,
            help="Describe what the service does and its key features",
            height=100,
        )

        # Buttons
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(
                "Save Changes",
                use_container_width=True,
                type="primary",
            )
        with col2:
            cancelled = st.form_submit_button(
                "Cancel",
                use_container_width=True,
            )

        if cancelled:
            if on_cancel:
                on_cancel()
            st.rerun()
            return

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

            # Build updates dict (only changed fields)
            updates: dict[str, str] = {}
            if service_name.strip() != service.service:
                updates["service"] = service_name.strip()
            if category.strip() != service.category:
                updates["category"] = category.strip()
            if description.strip() != service.description:
                updates["description"] = description.strip()

            if not updates:
                st.info("ℹ️ No changes detected.")
                return

            # Call the submission handler with original name and updates
            success = on_submit(service.service, updates)

            if success:
                st.success(f"✅ Service updated successfully!")
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


def display_edit_service_modal(
    service: ServiceData,
    on_submit: Callable[[str, dict[str, str]], bool],
    on_cancel: Callable[[], None] | None = None,
    categories: list[str] | None = None,
) -> None:
    """Display edit form in a modal/expander.

    Args:
        service: The service to edit.
        on_submit: Callback function to handle form submission.
        on_cancel: Optional callback to handle cancellation.
        categories: Optional list of existing categories.
    """
    with st.expander(f"✏️ Edit: {service.service}", expanded=True):
        display_edit_service_form(service, on_submit, on_cancel, categories)
