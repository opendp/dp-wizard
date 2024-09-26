from shiny import ui


def results_ui():
    return ui.nav_panel(
        "Download Results",
        "TODO: Download Results",
        ui.download_button("download_script", "Download script"),
        # TODO: Notebook code is badly formatted
        # ui.download_button(
        #     "download_notebook_unexecuted", "Download notebook (unexecuted)"
        # ),
        # ui.download_button(
        #     "download_notebook_executed", "Download notebook (executed)"
        # )
        value="results_panel",
    )
