import polars as pl
import opendp.prelude as dp

from dp_creator_ii.utils.mock_data import mock_data, ColumnDef

dp.enable_features("contrib")


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


def make_confidence_accuracy_histogram(
    lower=None, upper=None, bin_count=None, contributions=None, weighted_epsilon=None
):
    """
    Creates fake data between lower and upper, and then returns a DP histogram from it.
    >>> confidence, accuracy, histogram = make_confidence_accuracy_histogram(
    ...     lower=0, upper=10, bin_count=5, contributions=1, weighted_epsilon=1)
    >>> confidence
    0.95
    >>> accuracy
    3.37...
    >>> histogram
    shape: (5, 2)
    ┌─────────┬─────┐
    │ bin     ┆ len │
    │ ---     ┆ --- │
    │ str     ┆ u32 │
    ╞═════════╪═════╡
    │ (0, 2]  ┆ ... │
    │ (2, 4]  ┆ ... │
    │ (4, 6]  ┆ ... │
    │ (6, 8]  ┆ ... │
    │ (8, 10] ┆ ... │
    └─────────┴─────┘
    """
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
