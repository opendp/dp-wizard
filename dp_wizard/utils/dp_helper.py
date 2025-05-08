import polars as pl
import opendp.prelude as dp

from dp_wizard.utils.code_generators.analyses.histogram import (
    make_column_config_block as make_histogram_config_block,
)

dp.enable_features("contrib")


confidence = 0.95


def _make_cut_expr(
    column_name: str,
    lower_bound: float,
    upper_bound: float,
    bin_count: int,
):
    """
    >>> print(_make_cut_expr("abc", 0, 10, 5))
    col("abc").cut().alias("bin").strict_cast(String)

    """
    from dp_wizard.utils.shared import make_cut_points  # noqa: F401

    variables = globals()
    config_block = make_histogram_config_block(
        column_name=column_name,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        bin_count=bin_count,
    )
    config_block = config_block.replace(f"{column_name}_bin", "bin")
    exec(config_block, variables)
    return variables["bin_expr"]


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
    context = dp.Context.compositor(
        data=lf.with_columns(
            _make_cut_expr(
                column_name,
                lower_bound,
                upper_bound,
                bin_count,
            )
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
