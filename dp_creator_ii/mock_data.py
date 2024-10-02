from collections import namedtuple
import polars as pl

ColumnDef = namedtuple("ColumnDef", ["min", "max"])


def mock_data(column_defs, row_count=1000):
    schema = {column_name: float for column_name in column_defs.keys()}
    data = {column_name: [] for column_name in column_defs.keys()}
    for i in range(row_count):
        for column_name, column_def in column_defs.items():
            scale = column_def.max - column_def.min
            value = scale * i / row_count + column_def.min
            data[column_name].append(value)
    return pl.DataFrame(data=data, schema=schema)
