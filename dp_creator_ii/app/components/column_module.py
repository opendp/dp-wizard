from logging import info

from shiny import ui, render, module, reactive

from dp_creator_ii.utils.dp_helper import make_confidence_accuracy_histogram
from dp_creator_ii.app.components.plots import plot_histogram
from dp_creator_ii.utils.templates import make_column_config_block
from dp_creator_ii.app.components.outputs import output_code_sample, demo_tooltip


@module.ui
def column_ui():  # pragma: no cover
    width = "10em"  # Just wide enough so the text isn't trucated.
    return ui.layout_columns(
        [
            ui.output_ui("bounds_tooltip_ui"),
            ui.input_numeric("min", "Min", 0, width=width),
            ui.input_numeric("max", "Max", 10, width=width),
            ui.output_ui("bins_tooltip_ui"),
            ui.input_numeric("bins", "Bins", 10, width=width),
            ui.output_ui("weight_tooltip_ui"),
            ui.input_select(
                "weight",
                "Weight",
                choices={
                    1: "Less accurate",
                    2: "Default",
                    4: "More accurate",
                },
                selected=2,
                width=width,
            ),
        ],
        [
            # TODO: This doesn't need to be repeated: could just go once at the top.
            # https://github.com/opendp/dp-creator-ii/issues/138
            ui.markdown(
                "This simulation assumes a normal distribution "
                "between the specified min and max. "
                "Your data file has not been read except to determine the columns."
            ),
            ui.output_plot("column_plot", height="300px"),
            # Make plot smaller than default: about the same size as the other column.
            output_code_sample("Column Definition", "column_code"),
        ],
        col_widths={
            # Controls stay roughly a constant width;
            # Graph expands to fill space.
            "sm": (4, 8),
            "md": (3, 9),
            "lg": (2, 10),
        },
    )


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
    is_demo,
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

    @render.ui
    def bounds_tooltip_ui():
        return demo_tooltip(
            is_demo,
            """
            DP requires that we limit the sensitivity to the contributions
            of any individual. To do this, we need an estimate of the lower
            and upper bounds for each variable. We should not look at the
            data when estimating the bounds! In this case, we could imagine
            that "class year" would vary between 1 and 4, and we could limit
            "grade" to values between 50 and 100.
            """,
        )

    @render.ui
    def bins_tooltip_ui():
        return demo_tooltip(
            is_demo,
            """
            Different statistics can be measured with DP.
            This tool provides a histogram. If you increase the number of bins,
            you'll see that each individual bin becomes noisier to provide
            the same overall privacy guarantee. For this example, give
            "class_year" 4 bins and "grade" 5 bins.
            """,
        )

    @render.ui
    def weight_tooltip_ui():
        return demo_tooltip(
            is_demo,
            """
            You have a finite privacy budget, but you can choose
            how to allocate it. For simplicity, we limit the options here,
            but when using the library you can fine tune this.
            """,
        )

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
