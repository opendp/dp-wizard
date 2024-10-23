from shiny import ui, reactive, render

from dp_creator_ii.utils.argparse_helpers import get_csv_contrib
from dp_creator_ii.app.components.outputs import output_code_sample
from dp_creator_ii.utils.templates import make_privacy_unit_block


def dataset_ui():
    (_csv_path, contributions) = get_csv_contrib()

    return ui.nav_panel(
        "Select Dataset",
        ui.input_file("csv_path_from_ui", "Choose CSV file:", accept=[".csv"]),
        ui.markdown(
            "How many rows of the CSV can one individual contribute to? "
            'This is the "unit of privacy" which will be protected.'
        ),
        ui.input_numeric("contributions", "Contributions", contributions),
        output_code_sample("Unit of Privacy", "unit_of_privacy_python"),
        ui.input_action_button("go_to_analysis", "Define analysis"),
        value="dataset_panel",
    )


def dataset_server(input, output, session):  # pragma: no cover
    @render.code
    def unit_of_privacy_python():
        contributions = input.contributions()
        return make_privacy_unit_block(contributions)

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
