from logging import info

from shiny import ui, render, module, reactive

from dp_wizard.utils.dp_helper import make_confidence_accuracy_histogram
from dp_wizard.utils.shared import plot_histogram
from dp_wizard.utils.templates import make_column_config_block
from dp_wizard.app.components.outputs import output_code_sample, demo_tooltip


default_weight = 2

col_widths = {
    # Controls stay roughly a constant width;
    # Graph expands to fill space.
    "sm": (4, 8),
    "md": (3, 9),
    "lg": (2, 10),
}


@module.ui
def column_ui():  # pragma: no cover
    width = "10em"  # Just wide enough so the text isn't trucated.
    return ui.layout_columns(
        [
            # The initial values on these inputs
            # should be overridden by the reactive.effect.
            ui.input_numeric(
                "lower", ["Lower", ui.output_ui("bounds_tooltip_ui")], 0, width=width
            ),
            ui.input_numeric("upper", "Upper", 0, width=width),
            ui.input_numeric(
                "bins", ["Bins", ui.output_ui("bins_tooltip_ui")], 0, width=width
            ),
            ui.input_select(
                "weight",
                ["Weight", ui.output_ui("weight_tooltip_ui")],
                choices={
                    1: "Less accurate",
                    default_weight: "Default",
                    4: "More accurate",
                },
                selected=default_weight,
                width=width,
            ),
        ],
        [
            ui.output_plot("column_plot", height="300px"),
            # Make plot smaller than default: about the same size as the other column.
            output_code_sample("Column Definition", "column_code"),
        ],
        col_widths=col_widths,
    )


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
    is_demo,
):  # pragma: no cover
    @reactive.effect
    def _set_all_inputs():
        with reactive.isolate():  # Without isolate, there is an infinite loop.
            ui.update_numeric("lower", value=lower_bounds().get(name, 0))
            ui.update_numeric("upper", value=upper_bounds().get(name, 10))
            ui.update_numeric("bins", value=bin_counts().get(name, 10))
            ui.update_numeric("weight", value=weights().get(name, default_weight))

    @reactive.effect
    @reactive.event(input.lower)
    def _set_lower():
        lower_bounds.set({**lower_bounds(), name: float(input.lower())})

    @reactive.effect
    @reactive.event(input.upper)
    def _set_upper():
        upper_bounds.set({**upper_bounds(), name: float(input.upper())})

    @reactive.effect
    @reactive.event(input.bins)
    def _set_bins():
        bin_counts.set({**bin_counts(), name: float(input.bins())})

    @reactive.effect
    @reactive.event(input.weight)
    def _set_weight():
        weights.set({**weights(), name: float(input.weight())})

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
        return make_column_config_block(
            name=name,
            lower_bound=float(input.lower()),
            upper_bound=float(input.upper()),
            bin_count=int(input.bins()),
        )

    @render.plot()
    def column_plot():
        lower_x = float(input.lower())
        upper_x = float(input.upper())
        bin_count = int(input.bins())
        weight = float(input.weight())
        weights_sum = sum(weights().values())
        info(f"Weight ratio for {name}: {weight}/{weights_sum}")
        if weights_sum == 0:
            # This function is triggered when column is removed;
            # Exit early to avoid divide-by-zero.
            return None
        _confidence, accuracy, histogram = make_confidence_accuracy_histogram(
            lower=lower_x,
            upper=upper_x,
            bin_count=bin_count,
            contributions=contributions,
            weighted_epsilon=epsilon * weight / weights_sum,
        )
        return plot_histogram(
            histogram,
            error=accuracy,
            cutoff=0,  # TODO
        )
