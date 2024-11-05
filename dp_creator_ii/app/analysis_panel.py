from math import pow

from shiny import ui, reactive, render, req

from dp_creator_ii.app.components.inputs import log_slider
from dp_creator_ii.app.components.column_module import column_ui, column_server
from dp_creator_ii.utils.csv_helper import read_field_names
from dp_creator_ii.app.components.outputs import output_code_sample
from dp_creator_ii.utils.templates import make_privacy_loss_block


def analysis_ui():
    return ui.nav_panel(
        "Define Analysis",
        ui.markdown(
            "Select numeric columns of interest, "
            "and for each numeric column indicate the expected range, "
            "the number of bins for the histogram, "
            "and its relative share of the privacy budget."
        ),
        ui.input_checkbox_group("columns_checkbox_group", None, []),
        ui.output_ui("columns_ui"),
        ui.markdown(
            "What is your privacy budget for this release? "
            "Values above 1 will add less noise to the data, "
            "but have a greater risk of revealing individual data."
        ),
        log_slider("log_epsilon_slider", 0.1, 10.0),
        ui.output_text("epsilon_text"),
        output_code_sample("Privacy Loss", "privacy_loss_python"),
        ui.output_ui("download_results_button_ui"),
        value="analysis_panel",
    )


def _cleanup_reactive_dict(reactive_dict, keys_to_keep):
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
            choices=csv_fields_calc(),
        )

    @reactive.effect
    @reactive.event(input.columns_checkbox_group)
    def _on_column_set_change():
        column_ids_selected = input.columns_checkbox_group()
        _cleanup_reactive_dict(lower_bounds, column_ids_selected)
        _cleanup_reactive_dict(upper_bounds, column_ids_selected)
        _cleanup_reactive_dict(bin_counts, column_ids_selected)
        _cleanup_reactive_dict(weights, column_ids_selected)

    @render.ui
    def columns_ui():
        column_ids = input.columns_checkbox_group()
        for column_id in column_ids:
            column_server(
                column_id,
                name=column_id,
                contributions=contributions(),
                epsilon=epsilon(),
                lower_bounds=lower_bounds,
                upper_bounds=upper_bounds,
                bin_counts=bin_counts,
                weights=weights,
            )
        return [
            [
                ui.h3(column_id),
                column_ui(column_id),
            ]
            for column_id in column_ids
        ]

    @reactive.calc
    def csv_fields_calc():
        return read_field_names(req(csv_path()))

    @render.text
    def csv_fields():
        return csv_fields_calc()

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
