from pathlib import Path

from shiny import ui, reactive, render, Inputs, Outputs, Session

from dp_wizard.utils.argparse_helpers import get_cli_info
from dp_wizard.app.components.outputs import output_code_sample, demo_tooltip
from dp_wizard.utils.code_generators import make_privacy_unit_block


def dataset_ui():
    cli_info = get_cli_info()
    public_csv_placeholder = (
        "" if cli_info.public_csv_path is None else Path(cli_info.public_csv_path).name
    )
    private_csv_placeholder = (
        ""
        if cli_info.private_csv_path is None
        else Path(cli_info.private_csv_path).name
    )

    return ui.nav_panel(
        "Select Dataset",
        ui.card(
            ui.card_header("Input CSVs"),
            ui.markdown(
                """
    Choose **Public CSV** if you have a public data set, and are curious how
    DP can be applied: The preview visualizations will use your public data.

    Choose **Private CSV** if you only have a private data set, and want to
    make a release from it: The preview visualizations will only use
    simulated data, and apart from the headers, the private CSV is not
    read until the release.

    Choose both **Public CSV** and **Private CSV** if you have two files
    with the same structure. Perhaps the public CSV is older and no longer
    sensitive. Preview visualizations will be made with the public data,
    but the release will be made with private data.
    """
            ),
            # Doesn't seem to be possible to preset the actual value,
            # but the placeholder string is a good substitute.
            ui.input_file(
                "public_csv_path",
                ["Choose public CSV file", ui.output_ui("choose_csv_demo_tooltip_ui")],
                accept=[".csv"],
                placeholder=public_csv_placeholder,
            ),
            ui.input_file(
                "private_csv_path",
                "Choose private CSV file",
                accept=[".csv"],
                placeholder=private_csv_placeholder,
            ),
        ),
        ui.card(
            ui.card_header("Unit of privacy"),
            ui.markdown(
                "How many rows of the CSV can one individual contribute to? "
                'This is the "unit of privacy" which will be protected.'
            ),
            ui.input_numeric(
                "contributions",
                ["Contributions", ui.output_ui("contributions_demo_tooltip_ui")],
                cli_info.contributions,
                min=1,
            ),
            ui.output_ui("python_tooltip_ui"),
            output_code_sample("Unit of Privacy", "unit_of_privacy_python"),
        ),
        ui.output_ui("define_analysis_button_ui"),
        value="dataset_panel",
    )


def dataset_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    public_csv_path: reactive.Value[str],
    private_csv_path: reactive.Value[str],
    contributions: reactive.Value[int],
    is_demo: bool,
):  # pragma: no cover
    @reactive.effect
    @reactive.event(input.csv_path)
    def _on_csv_path_change():
        private_csv_path.set(input.csv_path()[0]["datapath"])

    @reactive.effect
    @reactive.event(input.contributions)
    def _on_contributions_change():
        contributions.set(input.contributions())

    @reactive.calc
    def button_enabled():
        contributions_is_set = input.contributions() is not None
        csv_path_is_set = (
            input.csv_path() is not None and len(input.csv_path()) > 0
        ) or is_demo
        return contributions_is_set and csv_path_is_set

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

    @render.ui
    def define_analysis_button_ui():
        button = ui.input_action_button(
            "go_to_analysis", "Define analysis", disabled=not button_enabled()
        )
        if button_enabled():
            return button
        return [
            button,
            "Choose CSV and Contributions before proceeding.",
        ]

    @render.code
    def unit_of_privacy_python():
        return make_privacy_unit_block(contributions())

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
