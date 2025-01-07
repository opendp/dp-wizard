from logging import info

from htmltools.tags import details, summary
from shiny import ui, render, module, reactive, Inputs, Outputs, Session
from shiny.types import SilentException

from dp_wizard.utils.dp_helper import make_accuracy_histogram
from dp_wizard.utils.shared import plot_histogram
from dp_wizard.utils.code_generators import make_column_config_block
from dp_wizard.app.components.outputs import output_code_sample
from dp_wizard.utils.dp_helper import confidence


@module.ui
def histogram_preview_ui():  # pragma: no cover
    return [
        ui.output_plot("histogram_preview_plot", height="300px"),
        ui.layout_columns(
            ui.output_text("confidence_accuracy_text"),
            details(
                summary("Data Table"),
                ui.output_data_frame("histogram_preview_data_frame"),
            ),
            output_code_sample("Column Definition", "column_code"),
        ),
    ]


@module.server
def histogram_preview_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    name: str,
    contributions: int,
    epsilon: float,
    row_count: int,
    weights: reactive.Value[dict[str, str]],
):  # pragma: no cover
    @render.text
    def confidence_accuracy_text():
        accuracy, histogram = accuracy_histogram()
        return f"The {confidence:.0%} confidence interval is ±{accuracy:.3g}."

    @render.data_frame
    def histogram_preview_data_frame():
        accuracy, histogram = accuracy_histogram()
        return render.DataGrid(histogram)

    @render.plot
    def histogram_preview_plot():
        accuracy, histogram = accuracy_histogram()
        s = "s" if contributions > 1 else ""
        title = (
            f"Simulated {name}: normal distribution, "
            f"{contributions} contribution{s} / invidual"
        )
        return plot_histogram(
            histogram,
            error=accuracy,
            cutoff=0,  # TODO
            title=title,
        )

    @render.code
    def column_code():
        return make_column_config_block(
            name=name,
            lower_bound=float(input.lower()),
            upper_bound=float(input.upper()),
            bin_count=int(input.bins()),
        )

    @reactive.calc()
    def accuracy_histogram():
        lower_x = float(input.lower())
        upper_x = float(input.upper())
        bin_count = int(input.bins())
        weight = float(input.weight())
        weights_sum = sum(float(weight) for weight in weights().values())
        info(f"Weight ratio for {name}: {weight}/{weights_sum}")
        if weights_sum == 0:
            # This function is triggered when column is removed;
            # Exit early to avoid divide-by-zero.
            raise SilentException("weights_sum == 0")
        accuracy_histogram = make_accuracy_histogram(
            row_count=row_count,
            lower=lower_x,
            upper=upper_x,
            bin_count=bin_count,
            contributions=contributions,
            weighted_epsilon=epsilon * weight / weights_sum,
        )
        return accuracy_histogram
