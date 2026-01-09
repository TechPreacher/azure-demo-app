"""Service list component for displaying Azure services.

Provides a table display of Azure services with sorting, selection, and actions.
"""

from typing import Callable

import pandas as pd
import streamlit as st

from src.api_client import ServiceData


def display_service_list(
    services: list[ServiceData],
    show_selection: bool = False,
    on_edit: Callable[[ServiceData], None] | None = None,
) -> ServiceData | None:
    """Display a table of Azure services.

    Args:
        services: List of services to display.
        show_selection: Whether to allow row selection.
        on_edit: Optional callback when edit is clicked for a service.

    Returns:
        Selected service if show_selection is True and a row is selected,
        otherwise None.
    """
    if not services:
        st.info("No services found matching your criteria.")
        return None

    # Convert to DataFrame for display
    df = pd.DataFrame([
        {
            "Service": svc.service,
            "Category": svc.category,
            "Description": svc.description,
        }
        for svc in services
    ])

    # Display service count
    st.markdown(f"**Found {len(services)} service(s)**")

    if show_selection:
        # Interactive table with selection
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            column_config={
                "Service": st.column_config.TextColumn(
                    "Service Name",
                    width="medium",
                ),
                "Category": st.column_config.TextColumn(
                    "Category",
                    width="small",
                ),
                "Description": st.column_config.TextColumn(
                    "Description",
                    width="large",
                ),
            },
        )

        # Return selected service if any
        if event and event.selection and event.selection.rows:
            selected_idx = event.selection.rows[0]
            return services[selected_idx]
        return None
    else:
        # Simple table display without selection
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Service": st.column_config.TextColumn(
                    "Service Name",
                    width="medium",
                ),
                "Category": st.column_config.TextColumn(
                    "Category",
                    width="small",
                ),
                "Description": st.column_config.TextColumn(
                    "Description",
                    width="large",
                ),
            },
        )
        return None


def display_service_detail(service: ServiceData) -> None:
    """Display detailed view of a single service.

    Args:
        service: Service to display.
    """
    st.subheader(f"📦 {service.service}")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("**Category:**")
        st.markdown("**Description:**")

    with col2:
        st.markdown(f"`{service.category}`")
        st.markdown(service.description)


def display_service_cards(
    services: list[ServiceData],
    on_edit: Callable[[ServiceData], None] | None = None,
) -> None:
    """Display services as expandable cards with optional edit button.

    Args:
        services: List of services to display.
        on_edit: Optional callback when edit is clicked for a service.
    """
    if not services:
        st.info("No services found matching your criteria.")
        return

    st.markdown(f"**Found {len(services)} service(s)**")

    for idx, service in enumerate(services):
        with st.expander(f"**{service.service}** - {service.category}"):
            st.markdown(service.description)

            if on_edit:
                if st.button(
                    "✏️ Edit",
                    key=f"edit_btn_{idx}",
                    help=f"Edit {service.service}",
                ):
                    on_edit(service)


def display_service_list_with_actions(
    services: list[ServiceData],
    on_edit: Callable[[ServiceData], None] | None = None,
) -> None:
    """Display services in a list format with action buttons.

    Args:
        services: List of services to display.
        on_edit: Optional callback when edit is clicked for a service.
    """
    if not services:
        st.info("No services found matching your criteria.")
        return

    st.markdown(f"**Found {len(services)} service(s)**")

    for idx, service in enumerate(services):
        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.markdown(f"**{service.service}**")
            st.caption(service.description[:100] + "..." if len(service.description) > 100 else service.description)

        with col2:
            st.markdown(f"`{service.category}`")

        with col3:
            if on_edit:
                if st.button(
                    "✏️",
                    key=f"edit_action_{idx}",
                    help=f"Edit {service.service}",
                ):
                    on_edit(service)

        st.divider()
