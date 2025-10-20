from shiny.ui import tags

from dp_wizard.shiny.components.icons import (
    data_source_icon,
    product_icon,
    unit_of_privacy_icon,
)
from dp_wizard.types import AppState


def dataset_summary(state: AppState):
    sources = []
    if state.private_csv_path():
        sources.append("Private CSV")
    if state.public_csv_path():
        sources.append("Public CSV")
    sources_str = ", ".join(sources)

    unit_of_privacy_str = (
        f"{state.contributions()} row / {state.contributions_entity()}"
    )

    product_str = state.product()

    return (
        tags.small(
            data_source_icon,
            f"Data Source: {sources_str}; ",
            unit_of_privacy_icon,
            f"Unit of Privacy: {unit_of_privacy_str}; ",
            product_icon,
            f"Product: {product_str}.",
            style="display: block; padding: 0 1em 1em 1em;",
        ),
    )
