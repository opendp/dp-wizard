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
        bin_count = config["bins"]
        # TODO: Increase the number of rows unless it impinges on performance?
        df = mock_data({name: ColumnDef(min_x, max_x)}, row_count=100)

        contributions = 10  # TODO: grab from top-level
        epsilon = 1  # TODO
        delta = 1e-7  # TODO

        # TODO: When this is stable, merge it to templates, so we can be
        # sure that we're using the same code in the preview that we
        # use in the generated notebook.
        cut_points = _make_cut_points(min_x, max_x, bin_count)
        context = dp.Context.compositor(
            data=pl.LazyFrame(df).with_columns(
                # The cut() method returns a Polars categorical type.
                # Cast to string to get the human-readable label.
                pl.col(name)
                .cut(cut_points)
                .alias(f"{name}_bin")
                .cast(pl.String),
            ),
            privacy_unit=dp.unit_of(contributions=contributions),
            privacy_loss=dp.loss_of(epsilon=epsilon, delta=delta),
            split_by_weights=[1],
            margins={
                (f"{name}_bin",): dp.polars.Margin(
                    max_partition_length=100,  # TODO: Use row_count above.
                    public_info="keys",
                ),
            },
        )
        query = context.query().group_by(f"{name}_bin").agg(pl.len().dp.noise())
        histogram = query.release().collect().sort(f"{name}_bin")

        return plot_histogram(
            histogram,
            error=5,  # TODO
            cutoff=0,  # TODO
        )
