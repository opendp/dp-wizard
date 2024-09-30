from pathlib import Path
import json
from shiny import ui, reactive, render
from dp_creator_ii import get_arg_parser
from htmltools.tags import details, pre, summary


def dataset_ui():
    args = get_arg_parser().parse_args()
    return ui.nav_panel(
        "Select Dataset",
        "TODO: Pick dataset",
        ui.output_text("csv_path_text"),
        ui.output_text("unit_of_privacy_text"),
        ui.input_numeric("contributions", "Contributions", args.unit_of_privacy),
        details(
            summary("Code sample"),
            pre(ui.output_text("unit_of_privacy_python")),
        ),
        ui.input_action_button("go_to_analysis", "Perform analysis"),
        value="dataset_panel",
    )


def dataset_server(input, output, session):
    args = get_arg_parser().parse_args()
    csv_path = reactive.value(args.csv_path)

    @render.text
    def csv_path_text():
        return str(csv_path.get())

    @render.text
    def unit_of_privacy_text():
        return input.contributions()

    @render.text
    def unit_of_privacy_python():
        contributions = input.contributions()
        return f"privacy_unit = dp.unit_of(contributions={contributions})"

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
