from sys import argv

from shiny import ui, reactive, render

from dp_creator_ii import get_arg_parser
from dp_creator_ii.app.ui_helpers import output_code_sample
from dp_creator_ii.template import make_privacy_unit


def get_args():
    arg_parser = get_arg_parser()
    if argv[1:3] == ["run", "--port"]:
        # We are running a Playwright test,
        # and ARGV is polluted, so override:
        return arg_parser.parse_args([])
    else:
        # Normal parsing:
        return arg_parser.parse_args()


def dataset_ui():
    args = get_args()

    return ui.nav_panel(
        "Select Dataset",
        "TODO: Pick dataset",
        ui.output_text("csv_path_text"),
        ui.input_numeric("contributions", "Contributions", args.contributions),
        output_code_sample("unit_of_privacy_python"),
        ui.input_action_button("go_to_analysis", "Define analysis"),
        value="dataset_panel",
    )


def dataset_server(input, output, session):
    args = get_args()

    csv_path = reactive.value(args.csv_path)

    @render.text
    def csv_path_text():
        return str(csv_path.get())

    @render.code
    def unit_of_privacy_python():
        contributions = input.contributions()
        return make_privacy_unit(contributions)

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
