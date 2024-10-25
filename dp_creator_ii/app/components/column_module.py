from shiny import ui, render, module, reactive
import opendp.prelude as dp
import polars as pl

from dp_creator_ii.utils.mock_data import mock_data, ColumnDef
from dp_creator_ii.app.components.plots import plot_histogram
from dp_creator_ii.utils.templates import make_column_config_block
from dp_creator_ii.app.components.outputs import output_code_sample

dp.enable_features("contrib")


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
        ui.markdown(
            "This simulation assumes a normal distribution "
            "between the specified min and max. "
            "Your data file has not been read except to determine the columns."
        ),
        ui.output_plot("column_plot"),
    ]


def _make_cut_points(lower, upper, bin_count):
    """
    Returns one more cut point than the bin_count.
    (There are actually two more bins, extending to
    -inf and +inf, but we'll ignore those.)
    Cut points are evenly spaced from lower to upper.

    >>> _make_cut_points(0, 10, 1)
    [0.0, 10.0]
    >>> _make_cut_points(0, 10, 2)
    [0.0, 5.0, 10.0]
    >>> _make_cut_points(0, 10, 3)
    [0.0, 3.33, 6.67, 10.0]
    """
    bin_width = (upper - lower) / bin_count
    return [round(lower + i * bin_width, 2) for i in range(bin_count + 1)]


@module.server
def column_server(
    input, output, session, name=None, contributions=None, epsilon=None
):  # pragma: no cover
    @reactive.calc
    def column_config():
        return {
            "min": input.min(),
            "max": input.max(),
            "bins": input.bins(),
            "weight": float(input.weight()),
            # TODO: We need to get the total of the weights across all columns,
            # so that we can calculate what proportion this column has,
            # and multiply that by the epsilon parameter.
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
        _confidence, accuracy, histogram = _make_confidence_accuracy_histogram(
            lower=min_x,
            upper=max_x,
            bin_count=bin_count,
            contributions=contributions,
            weighted_epsilon=epsilon * weight,  # TODO: Take into account all weights.
        )
        return plot_histogram(
            histogram,
            error=accuracy,
            cutoff=0,  # TODO
        )


def _make_confidence_accuracy_histogram(
    lower=None, upper=None, bin_count=None, contributions=None, weighted_epsilon=None
):
    # Mock data only depends on min and max, so it could be cached,
    # but I'd guess this is dominated by the DP operations,
    # so not worth optimizing.
    row_count = 100
    df = mock_data({"value": ColumnDef(lower, upper)}, row_count=row_count)

    # TODO: When this is stable, merge it to templates, so we can be
    # sure that we're using the same code in the preview that we
    # use in the generated notebook.
    cut_points = _make_cut_points(lower, upper, bin_count)
    context = dp.Context.compositor(
        data=pl.LazyFrame(df).with_columns(
            # The cut() method returns a Polars categorical type.
            # Cast to string to get the human-readable label.
            pl.col("value")
            .cut(cut_points)
            .alias("bin")
            .cast(pl.String),
        ),
        privacy_unit=dp.unit_of(
            contributions=contributions,
        ),
        privacy_loss=dp.loss_of(
            epsilon=weighted_epsilon,
            delta=1e-7,  # TODO
        ),
        split_by_weights=[1],
        margins={
            ("bin",): dp.polars.Margin(
                max_partition_length=row_count,
                public_info="keys",
            ),
        },
    )
    query = context.query().group_by("bin").agg(pl.len().dp.noise())

    confidence = 0.95
    accuracy = query.summarize(alpha=1 - confidence)["accuracy"].item()
    histogram = query.release().collect().sort("bin")
    return (confidence, accuracy, histogram)
