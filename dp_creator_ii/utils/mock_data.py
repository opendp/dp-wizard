from collections import namedtuple
import polars as pl
from scipy.stats import norm  # type: ignore

ColumnDef = namedtuple("ColumnDef", ["min", "max"])


def mock_data(column_defs, row_count=1000):
    schema = {column_name: float for column_name in column_defs.keys()}
    data = {column_name: [] for column_name in column_defs.keys()}

    # The details here don't really matter: Any method that
    # deterministically gave us more values in the middle of the range
    # and fewer at the extremes would do.
    quantile_width = 95 / 100
    for column_name, column_def in column_defs.items():
        min_ppf = norm.ppf((1 - quantile_width) / 2)
        max_ppf = norm.ppf(1 - (1 - quantile_width) / 2)
        min_value = column_def.min
        max_value = column_def.max
        slope = (max_value - min_value) / (max_ppf - min_ppf)
        intercept = min_value - slope * min_ppf
        for i in range(row_count):
            quantile = (quantile_width * i / (row_count - 1)) + (1 - quantile_width) / 2
            ppf = norm.ppf(quantile)
            value = slope * ppf + intercept
            data[column_name].append(value)
    return pl.DataFrame(data=data, schema=schema)
