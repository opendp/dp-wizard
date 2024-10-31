from pathlib import Path

from shiny import ui, reactive, render

from dp_creator_ii.utils.argparse_helpers import get_csv_contrib_from_cli
from dp_creator_ii.app.components.outputs import output_code_sample, demo_tooltip
from dp_creator_ii.utils.templates import make_privacy_unit_block


def dataset_ui():
    (csv_path, contributions, is_demo) = get_csv_contrib_from_cli()
    csv_placeholder = None if csv_path is None else Path(csv_path).name

    return ui.nav_panel(
        "Select Dataset",
        # Doesn't seem to be possible to preset the actual value,
        # but the placeholder string is a good substitute.
        ui.input_file(
            "csv_path",
            ["Choose CSV file", ui.output_ui("choose_csv_demo_tooltip_ui")],
            accept=[".csv"],
            placeholder=csv_placeholder,
        ),
        ui.markdown(
            "How many rows of the CSV can one individual contribute to? "
            'This is the "unit of privacy" which will be protected.'
        ),
        ui.input_numeric(
            "contributions",
            ["Contributions", ui.output_ui("contributions_demo_tooltip_ui")],
            contributions,
        ),
        ui.output_ui("python_tooltip_ui"),
        output_code_sample("Unit of Privacy", "unit_of_privacy_python"),
        ui.input_action_button("go_to_analysis", "Define analysis"),
        value="dataset_panel",
    )


def dataset_server(
    input, output, session, csv_path=None, contributions=None, is_demo=None
):  # pragma: no cover
    @reactive.effect
    @reactive.event(input.csv_path)
    def _on_csv_path_change():
        csv_path.set(input.csv_path()[0]["datapath"])

    @reactive.effect
    @reactive.event(input.contributions)
    def _on_contributions_change():
        contributions.set(input.contributions())

    @render.ui
    def choose_csv_demo_tooltip_ui():
        return demo_tooltip(
            is_demo,
            "For the demo, we'll imagine we have the grades "
            "on assignments for a class.",
        )

    @render.ui
    def contributions_demo_tooltip_ui():
        return demo_tooltip(
            is_demo,
            "For the demo, we assume that each student "
            f"can occur at most {contributions()} times in the dataset. ",
        )

    @render.ui
    def python_tooltip_ui():
        return demo_tooltip(
            is_demo,
            "Along the way, code samples will demonstrate "
            "how the information you provide is used in OpenDP, "
            "and at the end you can download a notebook "
            "for the entire calculation.",
        )

    @render.code
    def unit_of_privacy_python():
        return make_privacy_unit_block(contributions())

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
