from pathlib import Path

from shiny import ui, reactive, render

from dp_creator_ii.utils.argparse_helpers import get_csv_contrib_from_cli
from dp_creator_ii.app.components.outputs import output_code_sample
from dp_creator_ii.utils.template import make_privacy_unit_block


def dataset_ui():
    (csv_path, contributions) = get_csv_contrib_from_cli()
    csv_placeholder = None if csv_path is None else Path(csv_path).name

    return ui.nav_panel(
        "Select Dataset",
        # Doesn't seem to be possible to preset the actual value,
        # but the placeholder string is a good substitute.
        ui.input_file(
            "csv_path", "Choose CSV file:", accept=[".csv"], placeholder=csv_placeholder
        ),
        ui.markdown(
            "How many rows of the CSV can one individual contribute to? "
            'This is the "unit of privacy" which will be protected.'
        ),
        ui.input_numeric("contributions", "Contributions", contributions),
        output_code_sample("unit_of_privacy_python"),
        ui.input_action_button("go_to_analysis", "Define analysis"),
        value="dataset_panel",
    )


def dataset_server(
    input, output, session, csv_path=None, contributions=None
):  # pragma: no cover
    @reactive.effect
    @reactive.event(input.csv_path)
    def _on_csv_path_change():
        csv_path.set(input.csv_path()[0]["datapath"])

    @reactive.effect
    @reactive.event(input.contributions)
    def _on_contributions_change():
        contributions.set(input.contributions())

    @render.code
    def unit_of_privacy_python():
        return make_privacy_unit_block(contributions())

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
