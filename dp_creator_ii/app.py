import json
from pathlib import Path

from shiny import App, ui, reactive, render

config_path = Path(__file__).parent / "config.json"
config = json.loads(config_path.read_text())
config_path.unlink()

app_ui = ui.page_bootstrap(
    ui.navset_tab(
        ui.nav_panel(
            "Select Dataset",
            "TODO: Pick dataset",
            ui.output_text("csv_path_text"),
            ui.output_text("unit_of_privacy_text"),
            ui.input_action_button("go_to_analysis", "Perform analysis"),
            value="dataset_panel",
        ),
        ui.nav_panel(
            "Perform Analysis",
            "TODO: Define analysis",
            ui.input_action_button("go_to_results", "Download results"),
            value="analysis_panel",
        ),
        ui.nav_panel(
            "Download Results",
            "TODO: Download results",
            value="results_panel",
        ),
        id="top_level_nav",
    ),
    title="DP Creator II",
)


def server(input, output, session):
    csv_path = reactive.value(config["csv_path"])
    unit_of_privacy = reactive.value(config["unit_of_privacy"])

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

    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")


app = App(app_ui, server)
