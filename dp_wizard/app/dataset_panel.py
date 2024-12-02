from pathlib import Path

from shiny import ui, reactive, render, Inputs, Outputs, Session

from dp_wizard.utils.argparse_helpers import get_cli_info
from dp_wizard.app.components.outputs import output_code_sample, demo_tooltip
from dp_wizard.utils.code_generators import make_privacy_unit_block
from dp_wizard.app import analysis_panel
from dp_wizard.app.components.outputs import info_box

dataset_panel_id = "1_dataset_panel"


def dataset_ui():
    cli_info = get_cli_info()
    csv_placeholder = "" if cli_info.csv_path is None else Path(cli_info.csv_path).name

    return ui.nav_panel(
        "Select Dataset",
        ui.output_ui("dataset_panel_warning"),
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
            cli_info.contributions,
            min=1,
        ),
        ui.output_ui("python_tooltip_ui"),
        output_code_sample("Unit of Privacy", "unit_of_privacy_python"),
        ui.output_ui("define_analysis_button_ui"),
        value=dataset_panel_id,
    )


def dataset_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    csv_path: reactive.Value[str],
    contributions: reactive.Value[int],
    is_demo: bool,
    current_panel: reactive.Value[str],
):  # pragma: no cover
    @render.ui
    def dataset_panel_warning():
        if current_panel() > dataset_panel_id:
            return info_box(
                """
                Once you've confirmed your dataset and the unit of privacy
                they are locked. The unit of privacy is a characteristic
                of your dataset and shouldn't be tweaked just to improve
                utility.
                """
            )
        return ""

    @reactive.effect
    @reactive.event(input.csv_path)
    def _on_csv_path_change():
        csv_path.set(input.csv_path()[0]["datapath"])

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
            info_box("Choose CSV and Contributions before proceeding."),
        ]

    @render.code
    def unit_of_privacy_python():
        return make_privacy_unit_block(contributions())

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        current_panel.set(analysis_panel.analysis_panel_id)
        ui.update_navs("top_level_nav", selected=analysis_panel.analysis_panel_id)
