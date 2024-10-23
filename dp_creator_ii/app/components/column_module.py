from shiny import ui, render, module, reactive

from dp_creator_ii.utils.mock_data import mock_data, ColumnDef
from dp_creator_ii.app.components.plots import plot_error_bars_with_cutoff
from dp_creator_ii.utils.templates import make_column_config_block
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
        output_code_sample("Column Definition", "column_code"),
        ui.output_plot("column_plot"),
    ]


@module.server
def column_server(input, output, session):  # pragma: no cover
    @reactive.calc
    def column_config():
        return {
            # TODO: Is input._ns ok?
            # https://github.com/opendp/dp-creator-ii/issues/85
            "name": input._ns,
            "min": input.min(),
            "max": input.max(),
            "bins": input.bins(),
            "weight": float(input.weight()),
        }

    @render.code
    def column_code():
        config = column_config()
        return make_column_config_block(
            name=config["name"],
            min_value=config["min"],
            max_value=config["max"],
            bin_count=config["bins"],
        )

    @render.plot()
    def column_plot():
        config = column_config()
        name = config["name"]
        min_x = config["min"]
        max_x = config["max"]
        df = mock_data({name: ColumnDef(min_x, max_x)}, row_count=20)
        # TODO: we want to do DP with this data, not just return it raw.
        return plot_error_bars_with_cutoff(
            df[name].to_list(),
            x_min_label=min_x,
            x_max_label=max_x,
            y_cutoff=30,
            y_error=5,
        )
