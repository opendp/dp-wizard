from logging import info

import polars as pl
from htmltools.tags import details, summary
from shiny import module, render, ui, reactive
from shiny.types import SilentException

from dp_wizard.utils.dp_helper import confidence
from dp_wizard.utils.shared import plot_histogram
from dp_wizard.app.components.outputs import output_code_sample
from dp_wizard.utils.dp_helper import make_accuracy_histogram
from dp_wizard.utils.mock_data import mock_data, ColumnDef


@module.ui
def histogram_ui():
    return ui.output_ui("histogram_preview_ui")


@module.server
def histogram_server(
    input,
    output,
    session,
    name: str,
    row_count: int,
    contributions: int,
    epsilon: float,
    weights: reactive.Value[dict[str, str]],
    public_csv_path: str,
):
    @render.ui
    def histogram_preview_ui():
        accuracy, histogram = accuracy_histogram()
        return [
            ui.output_plot("histogram_preview_plot", height="300px"),
            ui.layout_columns(
                ui.markdown(
                    f"The {confidence:.0%} confidence interval is ±{accuracy:.3g}."
                ),
                details(
                    summary("Data Table"),
                    ui.output_data_frame("data_frame"),
                ),
                output_code_sample("Column Definition", "column_code"),
            ),
        ]

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

        # Mock data only depends on lower and upper bounds, so it could be cached,
        # but I'd guess this is dominated by the DP operations,
        # so not worth optimizing.
        # TODO: Use real public data, if we have it!
        if public_csv_path:
            lf = pl.scan_csv(public_csv_path)
        else:
            lf = pl.LazyFrame(
                mock_data({name: ColumnDef(lower_x, upper_x)}, row_count=row_count)
            )
        return make_accuracy_histogram(
            lf=lf,
            column_name=name,
            row_count=row_count,
            lower=lower_x,
            upper=upper_x,
            bin_count=bin_count,
            contributions=contributions,
            weighted_epsilon=epsilon * weight / weights_sum,
        )

    @render.data_frame
    def data_frame():
        accuracy, histogram = accuracy_histogram()
        return render.DataGrid(histogram)

    @render.plot
    def histogram_preview_plot():
        accuracy, histogram = accuracy_histogram()
        s = "s" if contributions > 1 else ""
        title = ", ".join(
            [
                name if public_csv_path else f"Simulated {name}: normal distribution",
                f"{contributions} contribution{s} / individual",
            ]
        )
        return plot_histogram(
            histogram,
            error=accuracy,
            cutoff=0,  # TODO
            title=title,
        )
