from logging import info

from htmltools.tags import details, summary
from shiny import ui, render, module, reactive, Inputs, Outputs, Session
from shiny.types import SilentException
import polars as pl

from dp_wizard.utils.dp_helper import make_accuracy_histogram
from dp_wizard.utils.shared import plot_histogram
from dp_wizard.utils.code_generators import make_column_config_block
from dp_wizard.app.components.outputs import output_code_sample, demo_tooltip, hide_if
from dp_wizard.utils.dp_helper import confidence
from dp_wizard.utils.mock_data import mock_data, ColumnDef


default_weight = "2"
label_width = "10em"  # Just wide enough so the text isn't trucated.


@module.ui
def column_ui():  # pragma: no cover
    col_widths = {
        # Controls stay roughly a constant width;
        # Graph expands to fill space.
        "sm": [4, 8],
        "md": [3, 9],
        "lg": [2, 10],
    }
    return ui.card(
        ui.card_header(ui.output_text("card_header")),
        ui.layout_columns(
            [
                # The initial values on these inputs
                # should be overridden by the reactive.effect.
                ui.input_numeric(
                    "lower",
                    ["Lower", ui.output_ui("bounds_tooltip_ui")],
                    0,
                    width=label_width,
                ),
                ui.input_numeric("upper", "Upper", 0, width=label_width),
                ui.input_numeric(
                    "bins",
                    ["Bins", ui.output_ui("bins_tooltip_ui")],
                    0,
                    width=label_width,
                ),
                ui.output_ui("optional_weight_ui"),
            ],
            ui.output_ui("histogram_preview_ui"),
            col_widths=col_widths,  # type: ignore
        ),
    )


@module.server
def column_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    public_csv_path: str,
    name: str,
    contributions: int,
    epsilon: float,
    row_count: int,
    lower_bounds: reactive.Value[dict[str, float]],
    upper_bounds: reactive.Value[dict[str, float]],
    bin_counts: reactive.Value[dict[str, int]],
    weights: reactive.Value[dict[str, str]],
    is_demo: bool,
    is_single_column: bool,
):  # pragma: no cover
    @reactive.effect
    def _set_all_inputs():
        with reactive.isolate():  # Without isolate, there is an infinite loop.
            ui.update_numeric("lower", value=lower_bounds().get(name, 0))
            ui.update_numeric("upper", value=upper_bounds().get(name, 10))
            ui.update_numeric("bins", value=bin_counts().get(name, 10))
            ui.update_numeric("weight", value=int(weights().get(name, default_weight)))

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
        bin_counts.set({**bin_counts(), name: int(input.bins())})

    @reactive.effect
    @reactive.event(input.weight)
    def _set_weight():
        weights.set({**weights(), name: input.weight()})

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

    @render.text
    def card_header():
        return name

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
    def optional_weight_ui():
        return hide_if(
            is_single_column,
            ui.input_select(
                "weight",
                ["Weight", ui.output_ui("weight_tooltip_ui")],
                choices={
                    "1": "Less accurate",
                    default_weight: "Default",
                    "4": "More accurate",
                },
                selected=default_weight,
                width=label_width,
            ),
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
                f"{contributions} contribution{s} / invidual",
            ]
        )
        return plot_histogram(
            histogram,
            error=accuracy,
            cutoff=0,  # TODO
            title=title,
        )
