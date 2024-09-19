import json
from pathlib import Path

from shiny import App, ui, reactive, render

config_path = Path(__file__).parent / 'config.json'
config = json.loads(config_path.read_text())

app_ui = ui.page_fluid(
    ui.output_text("value"),
    ui.navset_tab(  
        ui.nav_panel(
            "Dataset",
            "TODO: Pick dataset",
            ui.output_text("csv_path_text"),
            ui.output_text("unit_of_privacy_text")),
        ui.nav_panel("Analysis", "TODO: Define analysis"),
        ui.nav_panel("Download", "TODO: Download results"),
    )  
)


def server(input, output, session):
    csv_path = reactive.value(config['csv_path'])
    unit_of_privacy = reactive.value(config['unit_of_privacy'])

    @render.text
    def csv_path_text():
        return str(csv_path.get())

    @render.text
    def unit_of_privacy_text():
        return str(unit_of_privacy.get())


app = App(app_ui, server)
