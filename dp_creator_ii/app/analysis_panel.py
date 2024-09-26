from shiny import App, ui, reactive, render


def analysis_ui():
    return ui.nav_panel(
        "Perform Analysis",
        "TODO: Define analysis",
        ui.input_action_button("go_to_results", "Download results"),
        value="analysis_panel",
    )
