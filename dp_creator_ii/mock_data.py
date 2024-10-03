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
    quantile_width = 2 / 3
    for column_name, column_def in column_defs.items():
        scale = column_def.max - column_def.min
        center = (column_def.max + column_def.min) / 2
        for i in range(row_count):
            quantile = (quantile_width * i / (row_count - 1)) + (1 - quantile_width) / 2
            ppf = norm.ppf(quantile)
            value = ppf * scale / 2 + center
            data[column_name].append(value)
    return pl.DataFrame(data=data, schema=schema)
