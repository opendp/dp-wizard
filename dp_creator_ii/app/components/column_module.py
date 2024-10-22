from shiny import ui, render, module


@module.ui
def column_ui():  # pragma: no cover
    return [
        ui.input_numeric("min", "Min", 0),
        ui.input_numeric("max", "Max", 10),
        ui.input_numeric("bins", "Bins", 10),
        ui.input_select(
            "weight",
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
def column_server(input, output, session):  # pragma: no cover
    @output
    @render.code
    def col_config():
        return {
            "min": input.min(),
            "max": input.max(),
            "bins": input.bins(),
            "weight": input.weight(),
        }
