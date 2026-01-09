"""Filter components for searching and filtering services.

Provides UI components for filtering Azure services by category and search term.
"""

import streamlit as st

from src.api_client import ServiceData


def get_unique_categories(services: list[ServiceData]) -> list[str]:
    """Extract unique categories from services.

    Args:
        services: List of services.

    Returns:
        Sorted list of unique category names.
    """
    categories = set(svc.category for svc in services)
    return sorted(categories)


def display_filters(
    categories: list[str] | None = None,
) -> tuple[str | None, str | None]:
    """Display filter controls in sidebar.

    Args:
        categories: Optional list of categories for dropdown.
                   If None, only search filter is shown.

    Returns:
        Tuple of (selected_category, search_term).
        Values are None if not set.
    """
    st.sidebar.header("🔍 Filters")

    # Search input
    search_term = st.sidebar.text_input(
        "Search",
        placeholder="Search services...",
        help="Search in service names and descriptions",
    )

    # Category filter
    selected_category = None
    if categories:
        category_options = ["All Categories"] + categories
        category_choice = st.sidebar.selectbox(
            "Category",
            options=category_options,
            help="Filter by service category",
        )
        if category_choice != "All Categories":
            selected_category = category_choice

    # Clear filters button
    if st.sidebar.button("Clear Filters", use_container_width=True):
        # This will cause a rerun with cleared state
        st.rerun()

    return (
        selected_category if selected_category else None,
        search_term if search_term else None,
    )


def display_inline_filters(
    categories: list[str] | None = None,
) -> tuple[str | None, str | None]:
    """Display filter controls inline (not in sidebar).

    Args:
        categories: Optional list of categories for dropdown.

    Returns:
        Tuple of (selected_category, search_term).
    """
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        search_term = st.text_input(
            "Search",
            placeholder="Search services...",
            label_visibility="collapsed",
        )

    with col2:
        selected_category = None
        if categories:
            category_options = ["All Categories"] + categories
            category_choice = st.selectbox(
                "Category",
                options=category_options,
                label_visibility="collapsed",
            )
            if category_choice != "All Categories":
                selected_category = category_choice

    with col3:
        if st.button("🔄 Reset"):
            st.rerun()

    return (
        selected_category if selected_category else None,
        search_term if search_term else None,
    )
