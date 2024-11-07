from logging import info

from shiny import ui, render, module, reactive

from dp_creator_ii.utils.dp_helper import make_confidence_accuracy_histogram
from dp_creator_ii.app.components.plots import plot_histogram
from dp_creator_ii.utils.templates import make_column_config_block
from dp_creator_ii.app.components.outputs import output_code_sample


default_weight = 2


@module.ui
def column_ui():  # pragma: no cover
    return [
        # The default values on these inputs
        # should be overridden by the reactive.effect.
        ui.input_numeric("min", "Min", 0),
        ui.input_numeric("max", "Max", 0),
        ui.input_numeric("bins", "Bins", 0),
        ui.input_select(
            "weight",
            "Weight",
            choices={
                1: "Less accurate",
                default_weight: "Default",
                4: "More accurate",
            },
            selected=1,
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
    lower_bounds,
    upper_bounds,
    bin_counts,
    weights,
):  # pragma: no cover
    @reactive.effect
    def _set_all_inputs():
        with reactive.isolate():  # Without isolate, there is an infinite loop.
            ui.update_numeric("min", value=lower_bounds().get(name, 0))
            ui.update_numeric("max", value=upper_bounds().get(name, 10))
            ui.update_numeric("bins", value=bin_counts().get(name, 10))
            ui.update_numeric("weight", value=weights().get(name, default_weight))

    @reactive.effect
    @reactive.event(input.min)
    def _set_lower():
        lower_bounds.set({**lower_bounds(), name: float(input.min())})

    @reactive.effect
    @reactive.event(input.max)
    def _set_upper():
        upper_bounds.set({**upper_bounds(), name: float(input.max())})

    @reactive.effect
    @reactive.event(input.bins)
    def _set_bins():
        bin_counts.set({**bin_counts(), name: float(input.bins())})

    @reactive.effect
    @reactive.event(input.weight)
    def _set_weight():
        weights.set({**weights(), name: float(input.weight())})

    @render.code
    def column_code():
        return make_column_config_block(
            name=name,
            min_value=float(input.min()),
            max_value=float(input.max()),
            bin_count=int(input.bins()),
        )

    @render.plot()
    def column_plot():
        min_x = float(input.min())
        max_x = float(input.max())
        bin_count = int(input.bins())
        weight = float(input.weight())
        weights_sum = sum(weights().values())
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
