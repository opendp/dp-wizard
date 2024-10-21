from shiny import ui


def log_slider(id):
    return (
        ui.tags.table(
            ui.tags.tr(
                ui.tags.td("0.1"),
                ui.tags.td(
                    ui.input_slider(id, None, -1, 1, 0, step=0.1),
                ),
                ui.tags.td("10.0"),
            ),
        ),
    )
