from typing import NamedTuple
import polars as pl
from scipy.stats import norm


class ColumnDef(NamedTuple):
    lower_bound: float
    upper_bound: float


def mock_data(column_defs: dict[str, ColumnDef], row_count: int = 1000):
    """
    Return values from the inverse CDF of a normal distribution,
    so in the preview the only noise is from DP,
    not from randomly generated data.

    >>> col_0_100 = ColumnDef(0, 100)
    >>> col_neg_pos = ColumnDef(-10, 10)
    >>> df = mock_data({"col_0_100": col_0_100, "col_neg_pos": col_neg_pos})
    >>> df.select(pl.len()).item()
    1000

    Smallest value is slightly above the lower bound,
    so we don't get one isolated value in the lowest bin.
    >>> df.get_column("col_0_100")[0]
    0.4...
    >>> df.get_column("col_neg_pos")[0]
    -9.9...

    >>> df.get_column("col_0_100")[999]
    100.0
    >>> df.get_column("col_neg_pos")[999]
    10.0
    """
    schema = {column_name: float for column_name in column_defs.keys()}
    data = {column_name: [] for column_name in column_defs.keys()}

    quantile_width = 95 / 100
    for column_name, column_def in column_defs.items():
        lower_ppf = norm.ppf((1 - quantile_width) / 2)
        upper_ppf = norm.ppf(1 - (1 - quantile_width) / 2)
        lower_bound = column_def.lower_bound
        upper_bound = column_def.upper_bound
        slope = (upper_bound - lower_bound) / (upper_ppf - lower_ppf)
        intercept = lower_bound - slope * lower_ppf
        # Start from 1 instead of 0:
        # The polars bin intervals are closed at the top,
        # so if we include the zero, there is one value in the
        # (-inf, 0] bin.
        for i in range(1, row_count + 1):
            quantile = (quantile_width * i / (row_count)) + (1 - quantile_width) / 2
            ppf = norm.ppf(quantile)
            value = slope * ppf + intercept
            data[column_name].append(value)
    return pl.DataFrame(data=data, schema=schema)
