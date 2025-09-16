from math import pow
from pathlib import Path
from typing import Iterable

from htmltools import tags
from shiny import Inputs, Outputs, Session, reactive, render, ui

from dp_wizard import registry_url
from dp_wizard.shiny.components.column_module import column_server, column_ui
from dp_wizard.shiny.components.inputs import log_slider
from dp_wizard.shiny.components.outputs import (
    code_sample,
    hide_if,
    info_md_box,
    nav_button,
    tutorial_box,
)
from dp_wizard.types import AppState
from dp_wizard.utils.code_generators import make_privacy_loss_block
from dp_wizard.utils.csv_helper import (
    get_csv_row_count,
    id_labels_dict_from_names,
    id_names_dict_from_names,
)


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
                    "Columns",
                    [],
                    multiple=True,
                ),
                ui.output_ui("columns_selectize_tutorial_ui"),
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
                ui.output_ui("groups_selectize_tutorial_ui"),
            ),
            ui.card(
                ui.card_header("Privacy Budget"),
                ui.markdown(
                    f"""
                    What is your privacy budget for this release?
                    Many factors including the sensitivity of your data,
                    the frequency of DP releases,
                    and the regulatory landscape can be considered.
                    Consider how your budget compares to that of
                    <a href="{registry_url}"
                       target="_blank">other projects</a>.
                    """
                ),
                log_slider("log_epsilon_slider", 0.1, 10.0),
                ui.output_ui("epsilon_ui"),
                ui.output_ui("privacy_loss_python_ui"),
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
    reactive_dict: reactive.Value[dict], keys_to_keep: Iterable[str]
):  # pragma: no cover
    reactive_dict_copy = {**reactive_dict()}
    keys_to_del = set(reactive_dict_copy.keys()) - set(keys_to_keep)
    for key in keys_to_del:
        del reactive_dict_copy[key]
    reactive_dict.set(reactive_dict_copy)


def _trunc_pow(exponent):
    """
    The output should be roughly exponential,
    but should also be round numbers,
    so it doesn't seem too arbitrary to the user.
    >>> _trunc_pow(-1)
    0.1
    >>> _trunc_pow(-0.5)
    0.3
    >>> _trunc_pow(0)
    1.0
    >>> _trunc_pow(0.5)
    3.0
    >>> _trunc_pow(1)
    10.0
    """
    number = pow(10, exponent)
    return float(f"{number:.2g}" if abs(exponent) < 0.5 else f"{number:.1g}")


def analysis_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    state: AppState,
):  # pragma: no cover
    # CLI options:
    is_sample_csv = state.is_sample_csv
    # in_cloud = state.in_cloud

    # Top-lvel:
    is_tutorial_mode = state.is_tutorial_mode

    # Dataset choices:
    # initial_private_csv_path = state.initial_private_csv_path
    # private_csv_path = state.private_csv_path
    # initial_public_csv_path = state.initial_private_csv_path
    public_csv_path = state.public_csv_path
    contributions = state.contributions
    max_rows = state.max_rows

    # Analysis choices:
    column_names = state.column_names
    groups = state.groups
    epsilon = state.epsilon

    # Per-column choices:
    # (Note that these are all dicts, with the ColumnName as the key.)
    analysis_types = state.analysis_types
    lower_bounds = state.lower_bounds
    upper_bounds = state.upper_bounds
    bin_counts = state.bin_counts
    weights = state.weights
    analysis_errors = state.analysis_errors

    # Release state:
    # synthetic_data = state.synthetic_data
    released = state.released

    @reactive.calc
    def button_enabled():
        at_least_one_column = bool(weights())
        no_errors = not any(analysis_errors().values())
        return at_least_one_column and no_errors

    @reactive.effect
    def _update_columns():
        csv_ids_labels = {
            # Cast to string for type checking.
            str(k): v
            for k, v in csv_ids_labels_calc().items()
        }
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
    def groups_selectize_tutorial_ui():
        return tutorial_box(
            is_tutorial_mode(),
            """
            DP Wizard only supports the analysis of numeric data,
            but string values can be used for grouping.
            """,
            is_sample_csv,
            """
            With `sample.csv` you can select `class_year_str`
            to group results by class year.
            """,
            responsive=False,
        )

    @render.ui
    def columns_selectize_tutorial_ui():
        return tutorial_box(
            is_tutorial_mode(),
            """
            For each column you select here, a panel will appear below
            where you can configure the analysis for the column.
            Note that with more columns selected,
            each column has a smaller share of the privacy budget,
            and the accurace of results will go decline.
            """,
            is_sample_csv,
            """
            Not all columns need analysis.
            With `sample.csv`, you could just select `grade`.
            """,
            responsive=False,
        )

    @render.ui
    def simulation_card_ui():
        help = (
            tutorial_box(
                is_tutorial_mode(),
                """
                Unlike the other settings on this page,
                this estimate **is not used** in the final calculation.

                Until you make a release, your CSV will not be
                read except to determine the names columns,
                but the number of rows does have implications for the
                accuracy which DP can provide with a given privacy budget.
                """,
                responsive=False,
            ),
        )
        if public_csv_path():
            row_count_str = str(get_csv_row_count(Path(public_csv_path())))
            return [
                ui.markdown(
                    f"""
                    Because you've provided a public CSV,
                    it *will be read* to generate previews.

                    The confidence interval depends on the number of rows.
                    Your public CSV has {row_count_str} rows,
                    but if you believe the private CSV will be
                    much larger or smaller, please update.
                    """
                ),
                ui.input_select(
                    "row_count",
                    "Estimated Rows",
                    choices=[row_count_str, "100", "1000", "10000"],
                    selected=row_count_str,
                ),
                help,
            ]
        else:
            return [
                ui.markdown(
                    """
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
                help,
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
                contributions=contributions,
                epsilon=epsilon,
                row_count=int(input.row_count()),
                groups=groups,
                analysis_types=analysis_types,
                analysis_errors=analysis_errors,
                lower_bounds=lower_bounds,
                upper_bounds=upper_bounds,
                bin_counts=bin_counts,
                weights=weights,
                is_tutorial_mode=is_tutorial_mode,
                is_sample_csv=is_sample_csv,
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
        epsilon.set(_trunc_pow(input.log_epsilon_slider()))

    @render.ui
    def epsilon_ui():
        return tags.label(
            f"Epsilon: {epsilon()} ",
            tutorial_box(
                is_tutorial_mode(),
                """
                If you set epsilon above one, you'll see that the distribution
                becomes less noisy, and the confidence intervals become smaller...
                but increased accuracy risks revealing personal information.
                """,
                responsive=False,
            ),
        )

    @render.ui
    def privacy_loss_python_ui():
        return code_sample(
            "Privacy Loss",
            make_privacy_loss_block(
                pure=False, epsilon=epsilon(), max_rows=int(max_rows())
            ),
        )

    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")

    @render.ui
    def download_results_button_ui():
        is_enabled = button_enabled()
        button = nav_button(
            "go_to_results", "Download Results", disabled=not is_enabled
        )

        if is_enabled:
            return button
        return [
            button,
            "Select one or more columns before proceeding.",
        ]
