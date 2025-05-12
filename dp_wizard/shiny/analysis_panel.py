from math import pow
from typing import Iterable, Any
from pathlib import Path

from htmltools import tags
from shiny import ui, reactive, render, Inputs, Outputs, Session

from dp_wizard.shiny.components.inputs import log_slider
from dp_wizard.shiny.components.column_module import column_ui, column_server
from dp_wizard.utils.csv_helper import (
    id_names_dict_from_names,
    id_labels_dict_from_names,
    get_csv_row_count,
)
from dp_wizard.shiny.components.outputs import (
    output_code_sample,
    demo_tooltip,
    nav_button,
    hide_if,
    info_md_box,
)
from dp_wizard.utils.code_generators import make_privacy_loss_block


def analysis_ui():
    return ui.nav_panel(
        "Define Analysis",
        ui.output_ui("analysis_requirements_warning_ui"),
        ui.output_ui("analysis_release_warning_ui"),
        ui.layout_columns(
            ui.card(
                ui.card_header("Columns"),
                ui.markdown("Select columns to calculate statistics on."),
                ui.input_selectize(
                    "columns_selectize",
                    ["Columns", ui.output_ui("columns_selectize_tooltip_ui")],
                    [],
                    multiple=True,
                ),
            ),
            ui.card(
                ui.card_header("Grouping"),
                ui.markdown(
                    """
                    Select columns to group by, or leave empty
                    to calculate statistics across the entire dataset.

                    Groups aren't applied to the previews on this page
                    but will be used in the final release.
                    """
                ),
                ui.input_selectize(
                    "groups_selectize",
                    "Group by",
                    [],
                    multiple=True,
                ),
            ),
            ui.card(
                ui.card_header("Privacy Budget"),
                ui.markdown(
                    """
                    What is your privacy budget for this release?
                    Many factors including the sensitivity of your data,
                    the frequency of DP releases,
                    and the regulatory landscape can be considered.
                    Consider how your budget compares to that of
                    <a href="https://registry.oblivious.com/#public-dp"
                       target="_blank">other projects</a>.
                    """
                ),
                log_slider("log_epsilon_slider", 0.1, 10.0),
                ui.output_ui("epsilon_ui"),
                output_code_sample("Privacy Loss", "privacy_loss_python"),
            ),
            ui.card(
                ui.card_header("Simulation"),
                ui.output_ui("simulation_card_ui"),
            ),
            col_widths={
                "sm": [12, 12, 12, 12],  # 4 rows
                "md": [6, 6, 6, 6],  # 2 rows
                "xxl": [3, 3, 3, 3],  # 1 row
            },
        ),
        ui.output_ui("columns_ui"),
        ui.output_ui("download_results_button_ui"),
        value="analysis_panel",
    )


def _cleanup_reactive_dict(
    reactive_dict: reactive.Value[dict[str, Any]], keys_to_keep: Iterable[str]
):  # pragma: no cover
    reactive_dict_copy = {**reactive_dict()}
    keys_to_del = set(reactive_dict_copy.keys()) - set(keys_to_keep)
    for key in keys_to_del:
        del reactive_dict_copy[key]
    reactive_dict.set(reactive_dict_copy)


def analysis_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    released: reactive.Value[bool],
    public_csv_path: reactive.Value[str],
    # private_csv_path is not needed, since we have the column_names.
    column_names: reactive.Value[list[str]],
    contributions: reactive.Value[int],
    is_demo: bool,
    analysis_types: reactive.Value[dict[str, str]],
    lower_bounds: reactive.Value[dict[str, float]],
    upper_bounds: reactive.Value[dict[str, float]],
    bin_counts: reactive.Value[dict[str, int]],
    groups: reactive.Value[list[str]],
    weights: reactive.Value[dict[str, str]],
    epsilon: reactive.Value[float],
):  # pragma: no cover
    @reactive.calc
    def button_enabled():
        column_ids_selected = input.columns_selectize()
        return len(column_ids_selected) > 0

    @reactive.effect
    def _update_columns():
        csv_ids_labels = csv_ids_labels_calc()
        ui.update_selectize(
            "groups_selectize",
            label=None,
            choices=csv_ids_labels,
        )
        ui.update_selectize(
            "columns_selectize",
            label=None,
            choices=csv_ids_labels,
        )

    @reactive.effect
    @reactive.event(input.groups_selectize)
    def _on_groups_change():
        group_ids_selected = input.groups_selectize()
        column_ids_to_names = csv_ids_names_calc()
        groups.set([column_ids_to_names[id] for id in group_ids_selected])

    @render.ui
    def analysis_requirements_warning_ui():
        return hide_if(
            bool(column_names()),
            info_md_box(
                """
                Please select your dataset on the previous tab
                before defining your analysis.
                """
            ),
        )

    @render.ui
    def analysis_release_warning_ui():
        return hide_if(
            not released(),
            info_md_box(
                """
                After making a differentially private release,
                changes to the analysis will constitute a new release,
                and an additional epsilon spend.
                """
            ),
        )

    @reactive.effect
    @reactive.event(input.columns_selectize)
    def _on_columns_change():
        column_ids_selected = input.columns_selectize()
        # We only clean up the weights, and everything else is left in place,
        # so if you restore a column, you see the original values.
        # (Except for weight, which goes back to the default.)
        _cleanup_reactive_dict(weights, column_ids_selected)

    @render.ui
    def columns_selectize_tooltip_ui():
        return demo_tooltip(
            is_demo,
            """
            Not all columns need analysis. For this demo, just check
            "class_year" and "grade". With more columns selected,
            each column has a smaller share of the privacy budget.
            """,
        )

    @render.ui
    def simulation_card_ui():
        if public_csv_path():
            row_count = get_csv_row_count(Path(public_csv_path()))
            return [
                ui.markdown(
                    f"""
                    Because you've provided a public CSV,
                    it *will be read* to generate previews.

                    The confidence interval depends on the number of rows.
                    Your public CSV has {row_count} rows,
                    but if you believe the private CSV will be
                    much larger or smaller, please update.
                    """
                ),
                ui.input_select(
                    "row_count",
                    "Estimated Rows",
                    choices=[row_count, "100", "1000", "10000"],
                    selected=row_count,
                ),
            ]
        else:
            return [
                ui.markdown(
                    """
                    This simulation will assume a normal distribution
                    between the specified lower and upper bounds.
                    Until you make a release, your CSV will not be
                    read except to determine the columns.

                    What is the approximate number of rows in the dataset?
                    This number is only used for the simulation
                    and not the final calculation.
                    """
                ),
                ui.input_select(
                    "row_count",
                    "Estimated Rows",
                    choices=["100", "1000", "10000"],
                    selected="100",
                ),
            ]

    @render.ui
    def columns_ui():
        column_ids = input.columns_selectize()
        column_ids_to_names = csv_ids_names_calc()
        for column_id in column_ids:
            column_server(
                column_id,
                public_csv_path=public_csv_path(),
                name=column_ids_to_names[column_id],
                contributions=contributions(),
                epsilon=epsilon(),
                row_count=int(input.row_count()),
                analysis_types=analysis_types,
                lower_bounds=lower_bounds,
                upper_bounds=upper_bounds,
                bin_counts=bin_counts,
                weights=weights,
                is_demo=is_demo,
                is_single_column=len(column_ids) == 1,
            )
        return [column_ui(column_id) for column_id in column_ids]

    @reactive.calc
    def csv_ids_names_calc():
        return id_names_dict_from_names(column_names())

    @reactive.calc
    def csv_ids_labels_calc():
        return id_labels_dict_from_names(column_names())

    @reactive.effect
    @reactive.event(input.log_epsilon_slider)
    def _set_epsilon():
        epsilon.set(pow(10, input.log_epsilon_slider()))

    @render.ui
    def epsilon_ui():
        return tags.label(
            f"Epsilon: {epsilon():0.3} ",
            demo_tooltip(
                is_demo,
                """
                If you set epsilon above one, you'll see that the distribution
                becomes less noisy, and the confidence intervals become smaller...
                but increased accuracy risks revealing personal information.
                """,
            ),
        )

    @render.code
    def privacy_loss_python():
        return make_privacy_loss_block(epsilon())

    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")

    @render.ui
    def download_results_button_ui():
        button = nav_button(
            "go_to_results", "Download Results", disabled=not button_enabled()
        )

        if button_enabled():
            return button
        return [
            button,
            "Select one or more columns before proceeding.",
        ]
