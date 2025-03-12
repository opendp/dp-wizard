from pathlib import Path
from typing import Optional

from shiny import ui, reactive, render, Inputs, Outputs, Session

from dp_wizard.utils.argparse_helpers import (
    get_cli_info,
    PUBLIC_TEXT,
    PRIVATE_TEXT,
    PUBLIC_PRIVATE_TEXT,
)
from dp_wizard.utils.csv_helper import get_csv_names_mismatch
from dp_wizard.app.components.outputs import (
    output_code_sample,
    demo_tooltip,
    hide_if,
    info_box,
)
from dp_wizard.utils.code_generators import make_privacy_unit_block


def about_ui():
    return ui.nav_panel(
        "About",
        ui.card(
            ui.card_header("About DP Wizard"),
            ui.markdown(
                """
                DP Wizard guides the user through the application of
                differential privacy. After selecting a local CSV,
                users are prompted to describe to the anlysis they need.
                Output options include:
                - A Jupyter notebook which demonstrates how to use
                [OpenDP](https://docs.opendp.org/).
                - A plain Python script.
                - Text and CSV reports.
                """
            ),
        ),
        ui.input_action_button("go_to_dataset", "Select dataset"),
        value="about_panel",
    )


def about_server(
    input: Inputs,
    output: Outputs,
    session: Session,
):  # pragma: no cover
    @reactive.effect
    @reactive.event(input.go_to_dataset)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="dataset_panel")
