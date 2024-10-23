from shiny import ui, render, module, reactive

from dp_creator_ii.utils.template import make_column_config_block
from dp_creator_ii.app.components.outputs import output_code_sample


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
        output_code_sample("column_code"),
    ]


@module.server
def column_server(input, output, session):  # pragma: no cover
    @reactive.calc
    def column_config():
        return {
            "min": input.min(),
            "max": input.max(),
            "bins": input.bins(),
            "weight": float(input.weight()),
        }

    @render.code
    def column_code():
        config = column_config()
        return make_column_config_block(
            name="TODO",
            min_value=config["min"],
            max_value=config["max"],
            bin_count=config["bins"],
        )
