from sys import argv

from shiny import ui, reactive, render

from dp_creator_ii import get_arg_parser


def dataset_ui():
    return ui.nav_panel(
        "Select Dataset",
        "TODO: Pick dataset",
        ui.input_file("csv_path_from_ui", "Choose CSV file", accept=[".csv"]),
        "CSV path from either CLI or UI:",
        ui.output_text("csv_path"),
        ui.output_text("unit_of_privacy_text"),
        ui.input_action_button("go_to_analysis", "Define analysis"),
        value="dataset_panel",
    )


def dataset_server(input, output, session):
    if argv[1:3] == ["run", "--port"]:
        # Started by playwright
        arg_csv_path = None
        arg_unit_of_privacy = None
    else:
        args = get_arg_parser().parse_args()
        arg_csv_path = args.csv_path
        arg_unit_of_privacy = args.unit_of_privacy

    csv_path_from_cli_value = reactive.value(arg_csv_path)
    unit_of_privacy = reactive.value(arg_unit_of_privacy)

    @render.text
    def csv_path():
        if input.csv_path_from_ui() is not None:
            return input.csv_path_from_ui()[0]["datapath"]
        return csv_path_from_cli_value.get()

    @render.text
    def unit_of_privacy_text():
        return str(unit_of_privacy.get())

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
