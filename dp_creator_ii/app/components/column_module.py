from shiny import ui, render, module


@module.ui
def col_ui():
    return [
        ui.input_numeric(f"min", "Min", 0),
        ui.input_numeric(f"max", "Max", 10),
        ui.input_numeric(f"bins", "Bins", 10),
        ui.input_select(
            f"weight",
            "Weight",
            choices={
                1: "Least accurate",
                2: "Less accurate",
                4: "More accurate",
                8: "Most accurate",
            },
        ),
        ui.output_code("col_config"),
    ]


@module.server
def col_server(input, output, session):  # pragma: no cover
    @output
    @render.code
    def col_config():
        return {
            "min": input.min(),
            "max": input.max(),
            "bins": input.bins(),
            "weight": input.weight(),
        }
