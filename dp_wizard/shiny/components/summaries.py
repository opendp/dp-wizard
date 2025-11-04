from shiny.ui import tags

from dp_wizard.shiny.components.icons import (
    budget_icon,
    columns_icon,
    data_source_icon,
    groups_icon,
    product_icon,
    unit_of_privacy_icon,
)
from dp_wizard.types import AppState

_css = "display: block; padding: 0 1em 1em 1em;"


def dataset_summary(state: AppState):  # pragma: no cover
    sources = []
    if state.private_csv_path():
        sources.append("Private CSV")
    if state.public_csv_path():
        sources.append("Public CSV")
    if state.in_cloud:
        sources.append("Field List")

    contributions = state.contributions()
    entity = state.contributions_entity()
    s = "s" if contributions > 1 else ""
    unit_of_privacy = f"{contributions} row{s} / {entity}"

    product = state.product()

    return tags.small(
        data_source_icon,
        f"Data Source: {', '.join(sources)}; ",
        unit_of_privacy_icon,
        f"Unit of Privacy: {unit_of_privacy}; ",
        product_icon,
        f"Product: {product}.",
        style=_css,
    )


def analysis_summary(state: AppState):  # pragma: no cover
    columns = (
        ", ".join(
            f"{analysis} of {column}"
            for column, analysis in state.analysis_types().items()
        )
        or "None"
    )
    groups = ", ".join(state.groups()) or "None"
    budget = state.epsilon()

    return tags.small(
        columns_icon,
        f"Columns: {columns}; ",
        groups_icon,
        f"Groups: {groups}; ",
        budget_icon,
        f"Privacy Budget: {budget} epsilon.",
        style=_css,
    )
