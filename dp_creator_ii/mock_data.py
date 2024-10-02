from collections import namedtuple
import polars as pl
from scipy.stats import norm

ColumnDef = namedtuple("ColumnDef", ["min", "max"])


def mock_data(column_defs, row_count=1000):
    schema = {column_name: float for column_name in column_defs.keys()}
    data = {column_name: [] for column_name in column_defs.keys()}
    for i in range(row_count + 1):
        for column_name, column_def in column_defs.items():
            quantile_width = 2 / 3
            quantile = (quantile_width * i / row_count) + (1 - quantile_width) / 2
            ppf = norm.ppf(quantile)
            scale = column_def.max - column_def.min
            center = (column_def.max + column_def.min) / 2
            value = ppf * scale / 2 + center
            data[column_name].append(value)
    return pl.DataFrame(data=data, schema=schema)
