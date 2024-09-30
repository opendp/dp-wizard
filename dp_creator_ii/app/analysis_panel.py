from shiny import ui, reactive


def analysis_ui():
    return ui.nav_panel(
        "Perform Analysis",
        "TODO: Define analysis",
        ui.input_action_button("go_to_results", "Download results"),
        value="analysis_panel",
    )


def analysis_server(input, output, session):
    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")
