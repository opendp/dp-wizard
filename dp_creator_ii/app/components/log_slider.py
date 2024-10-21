from shiny import ui


def log_slider():
    return (
        ui.tags.table(
            ui.tags.tr(
                ui.tags.td("0.1"),
                ui.tags.td(
                    ui.input_slider("log_epsilon_slider", None, -1, 1, 0, step=0.1),
                ),
                ui.tags.td("10.0"),
            ),
        ),
    )
