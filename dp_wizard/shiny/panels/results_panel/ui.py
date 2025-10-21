from shiny import ui


def results_ui():  # pragma: no cover
    return ui.nav_panel(
        "Download Results",
        ui.output_ui("results_requirements_warning_ui"),
        ui.output_ui("synthetic_data_ui"),
        ui.output_ui("custom_download_stem_ui"),
        ui.output_ui("download_results_ui"),
        ui.output_ui("download_code_ui"),
        value="results_panel",
    )
