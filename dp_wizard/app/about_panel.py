import sys
from pathlib import Path

from shiny import ui, reactive, Inputs, Outputs, Session

from dp_wizard.app.components.outputs import nav_button


def about_ui():
    version = (Path(__file__).parent.parent / "VERSION").read_text()
    return ui.nav_panel(
        "About",
        ui.card(
            ui.card_header("About DP Wizard"),
            ui.markdown(
                """
                DP Wizard guides you through the application of
                differential privacy. After selecting a local CSV,
                you'll be prompted to describe the analysis you need.
                Output options include:
                - A Jupyter notebook which demonstrates how to use
                [OpenDP](https://docs.opendp.org/).
                - A plain Python script.
                - Text and CSV reports.
                """
            ),
            ui.p(f"DP Wizard version {version}"),
            ui.p(f"Python {sys.version}"),
        ),
        nav_button("go_to_dataset", "Select dataset"),
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
