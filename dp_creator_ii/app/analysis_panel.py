from math import pow

from shiny import ui, reactive, render, req

from dp_creator_ii.app.components.inputs import log_slider
from dp_creator_ii.app.components.column_module import column_ui, column_server
from dp_creator_ii.utils.csv_helper import read_csv_ids_labels, read_csv_ids_names
from dp_creator_ii.app.components.outputs import output_code_sample, demo_tooltip
from dp_creator_ii.utils.templates import make_privacy_loss_block
from dp_creator_ii.app.components.column_module import col_widths


def analysis_ui():
    return ui.nav_panel(
        "Define Analysis",
        ui.markdown(
            "Select numeric columns of interest, "
            "and for each numeric column indicate the expected range, "
            "the number of bins for the histogram, "
            "and its relative share of the privacy budget."
        ),
        ui.input_checkbox_group(
            "columns_checkbox_group",
            ["Columns", ui.output_ui("columns_checkbox_group_tooltip_ui")],
            [],
        ),
        ui.output_ui("columns_ui"),
        ui.markdown(
            "What is your privacy budget for this release? "
            "Values above 1 will add less noise to the data, "
            "but have a greater risk of revealing individual data."
        ),
        ui.output_ui("epsilon_tooltip_ui"),
        log_slider("log_epsilon_slider", 0.1, 10.0),
        ui.output_text("epsilon_text"),
        output_code_sample("Privacy Loss", "privacy_loss_python"),
        ui.output_ui("download_results_button_ui"),
        value="analysis_panel",
    )


def _cleanup_reactive_dict(reactive_dict, keys_to_keep):  # pragma: no cover
    reactive_dict_copy = {**reactive_dict()}
    keys_to_del = set(reactive_dict_copy.keys()) - set(keys_to_keep)
    for key in keys_to_del:
        del reactive_dict_copy[key]
    reactive_dict.set(reactive_dict_copy)


def analysis_server(
    input,
    output,
    session,
    csv_path,
    contributions,
    is_demo,
    lower_bounds,
    upper_bounds,
    bin_counts,
    weights,
    epsilon,
):  # pragma: no cover
    @reactive.calc
    def button_enabled():
        column_ids_selected = input.columns_checkbox_group()
        return len(column_ids_selected) > 0

    @reactive.effect
    def _update_checkbox_group():
        ui.update_checkbox_group(
            "columns_checkbox_group",
            label=None,
            choices=csv_ids_labels_calc(),
        )

    @reactive.effect
    @reactive.event(input.columns_checkbox_group)
    def _on_column_set_change():
        column_ids_selected = input.columns_checkbox_group()
        # We only clean up the weights, and everything else is left in place,
        # so if you restore a column, you see the original values.
        # (Except for weight, which goes back to the default.)
        _cleanup_reactive_dict(weights, column_ids_selected)

    @render.ui
    def columns_checkbox_group_tooltip_ui():
        return demo_tooltip(
            is_demo,
            """
            Not all columns need analysis. For this demo, just check
            "class_year" and "grade". With more columns selected,
            each column has a smaller share of the privacy budget.
            """,
        )

    @render.ui
    def columns_ui():
        column_ids = input.columns_checkbox_group()
        column_ids_to_names = csv_ids_names_calc()
        column_ids_to_labels = csv_ids_labels_calc()
        for column_id in column_ids:
            column_server(
                column_id,
                name=column_ids_to_names[column_id],
                contributions=contributions(),
                epsilon=epsilon(),
                lower_bounds=lower_bounds,
                upper_bounds=upper_bounds,
                bin_counts=bin_counts,
                weights=weights,
                is_demo=is_demo,
            )
        return [
            [
                [
                    ui.h3(column_ids_to_labels[column_id]),
                    column_ui(column_id),
                ]
                for column_id in column_ids
            ],
            [
                (
                    ui.layout_columns(
                        [],
                        [
                            ui.markdown(
                                """
                            This simulation assumes a normal
                            distribution between the specified
                            lower and upper bounds. Your data
                            file has not been read except to
                            determine the columns.
                            """
                            )
                        ],
                        col_widths=col_widths,
                    )
                    if column_ids
                    else []
                )
            ],
        ]

    @reactive.calc
    def csv_ids_names_calc():
        return read_csv_ids_names(req(csv_path()))

    @reactive.calc
    def csv_ids_labels_calc():
        return read_csv_ids_labels(req(csv_path()))

    @render.ui
    def epsilon_tooltip_ui():
        return demo_tooltip(
            is_demo,
            """
            If you set epsilon above one, you'll see that the distribution
            becomes less noisy, and the confidence intervals become smaller...
            but increased accuracy risks revealing personal information.
            """,
        )

    @reactive.effect
    @reactive.event(input.log_epsilon_slider)
    def _set_epsilon():
        epsilon.set(pow(10, input.log_epsilon_slider()))

    @render.text
    def epsilon_text():
        return f"Epsilon: {epsilon():0.3}"

    @render.code
    def privacy_loss_python():
        return make_privacy_loss_block(epsilon())

    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")

    @render.ui
    def download_results_button_ui():
        button = ui.input_action_button(
            "go_to_results", "Download results", disabled=not button_enabled()
        )

        if button_enabled():
            return button
        return [
            button,
            "Select one or more columns before proceeding.",
        ]
