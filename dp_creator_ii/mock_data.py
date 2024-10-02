from collections import namedtuple
import polars as pl
from scipy.stats import norm

ColumnDef = namedtuple("ColumnDef", ["min", "max"])


def mock_data(column_defs, row_count=1000):
    schema = {column_name: float for column_name in column_defs.keys()}
    data = {column_name: [] for column_name in column_defs.keys()}
    for i in range(row_count):
        for column_name, column_def in column_defs.items():
            quantile = i / row_count / 2 + 0.25  # ie, 25th to 75th percentiles
            value = norm.ppf(quantile)
            data[column_name].append(value)
    return pl.DataFrame(data=data, schema=schema)
