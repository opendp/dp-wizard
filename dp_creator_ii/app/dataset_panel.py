from shiny import App, ui, module, reactive, render


def dataset_ui():
    return ui.nav_panel(
        "Select Dataset",
        "TODO: Pick dataset",
        ui.output_text("csv_path_text"),
        ui.output_text("unit_of_privacy_text"),
        ui.input_action_button("go_to_analysis", "Perform analysis"),
        value="dataset_panel",
    )
