from logging import info

from shiny import ui, render, module, reactive

from dp_creator_ii.utils.dp_helper import make_confidence_accuracy_histogram
from dp_creator_ii.app.components.plots import plot_histogram
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
                1: "Less accurate",
                2: "Default",
                4: "More accurate",
            },
            selected=2,
        ),
        output_code_sample("Column Definition", "column_code"),
        ui.markdown(
            "This simulation assumes a normal distribution "
            "between the specified min and max. "
            "Your data file has not been read except to determine the columns."
        ),
        ui.output_plot("column_plot"),
    ]


@module.server
def column_server(
    input,
    output,
    session,
    name,
    contributions,
    epsilon,
    set_column_weight,
    get_weights_sum,
):  # pragma: no cover
    @reactive.effect
    @reactive.event(input.weight)
    def _():
        set_column_weight(name, float(input.weight()))

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
            name=name,
            min_value=config["min"],
            max_value=config["max"],
            bin_count=config["bins"],
        )

    @render.plot()
    def column_plot():
        config = column_config()
        min_x = config["min"]
        max_x = config["max"]
        bin_count = config["bins"]
        weight = config["weight"]
        weights_sum = get_weights_sum()
        info(f"Weight ratio for {name}: {weight}/{weights_sum}")
        if weights_sum == 0:
            # This function is triggered when column is removed;
            # Exit early to avoid divide-by-zero.
            return None
        _confidence, accuracy, histogram = make_confidence_accuracy_histogram(
            lower=min_x,
            upper=max_x,
            bin_count=bin_count,
            contributions=contributions,
            weighted_epsilon=epsilon * weight / weights_sum,
        )
        return plot_histogram(
            histogram,
            error=accuracy,
            cutoff=0,  # TODO
        )
