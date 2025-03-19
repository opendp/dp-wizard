import polars as pl
import opendp.prelude as dp

from dp_wizard.utils.shared import make_cut_points

dp.enable_features("contrib")


confidence = 0.95


def make_accuracy_histogram(
    lf: pl.LazyFrame,
    column_name: str,
    row_count: int,
    lower_bound: float,
    upper_bound: float,
    bin_count: int,
    contributions: int,
    weighted_epsilon: float,
) -> tuple[float, pl.DataFrame]:
    """
    Given a LazyFrame and column, and calculate a DP histogram.

    >>> from dp_wizard.utils.mock_data import mock_data, ColumnDef
    >>> lower_bound, upper_bound = 0, 10
    >>> row_count = 100
    >>> column_name = "value"
    >>> df = mock_data(
    ...     {column_name: ColumnDef(lower_bound, upper_bound)},
    ...     row_count=row_count
    ... )
    >>> accuracy, histogram = make_accuracy_histogram(
    ...     lf=pl.LazyFrame(df),
    ...     column_name=column_name,
    ...     row_count=100,
    ...     lower_bound=0, upper_bound=10,
    ...     bin_count=5,
    ...     contributions=1,
    ...     weighted_epsilon=1
    ... )
    >>> accuracy
    3.37...
    >>> histogram.sort("bin")
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
    # TODO: https://github.com/opendp/dp-wizard/issues/219
    # When this is stable, merge it to templates, so we can be
    # sure that we're using the same code in the preview that we
    # use in the generated notebook.
    cut_points = make_cut_points(lower_bound, upper_bound, bin_count)
    context = dp.Context.compositor(
        data=lf.with_columns(
            # The cut() method returns a Polars categorical type.
            # Cast to string to get the human-readable label.
            pl.col(column_name)
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
        margins=[
            dp.polars.Margin(  # type: ignore
                by=["bin"],
                max_partition_length=row_count,
                public_info="keys",
            ),
        ],
    )
    query = context.query().group_by("bin").agg(pl.len().dp.noise())  # type: ignore

    accuracy = query.summarize(alpha=1 - confidence)["accuracy"].item()  # type: ignore
    histogram = query.release().collect()
    return (accuracy, histogram)
