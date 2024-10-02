from sys import argv

from shiny import ui, reactive, render

from dp_creator_ii import get_arg_parser


def dataset_ui():
    return ui.nav_panel(
        "Select Dataset",
        "TODO: Pick dataset",
        ui.output_text("csv_path_text"),
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

    csv_path = reactive.value(arg_csv_path)
    unit_of_privacy = reactive.value(arg_unit_of_privacy)

    @render.text
    def csv_path_text():
        return str(csv_path.get())

    @render.text
    def unit_of_privacy_text():
        return str(unit_of_privacy.get())

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
