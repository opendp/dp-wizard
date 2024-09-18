from shiny import App, ui

app_ui = ui.page_fluid(
    ui.navset_tab(  
        ui.nav_panel("Dataset", "TODO: Pick dataset"),
        ui.nav_panel("Analysis", "TODO: Define analysis"),
        ui.nav_panel("Download", "TODO: Download results"),
    )  
)


def server(input, output, session):
    pass


app = App(app_ui, server)
