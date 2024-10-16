from sys import argv

from shiny import ui, reactive, render

from dp_creator_ii import get_arg_parser
from dp_creator_ii.app.ui_helpers import output_code_sample
from dp_creator_ii.template import make_privacy_unit_block


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
        ui.input_file("csv_path_from_ui", "Choose CSV file:", accept=[".csv"]),
        ui.markdown(
            "How many rows of the CSV can one individual contribute to? "
            'This is the "unit of privacy" which will be protected.'
        ),
        ui.input_numeric("contributions", "Contributions", args.contributions),
        output_code_sample("unit_of_privacy_python"),
        ui.input_action_button("go_to_analysis", "Define analysis"),
        value="dataset_panel",
    )


def dataset_server(input, output, session):
    args = get_args()

    csv_path_from_cli_value = reactive.value(args.csv_path)

    @render.code
    def unit_of_privacy_python():
        contributions = input.contributions()
        return make_privacy_unit_block(contributions)

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
