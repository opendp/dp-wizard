import polars as pl
from pytest import approx

from dp_creator_ii.mock_data import mock_data, ColumnDef


def test_mock_data():
    col_0_100 = ColumnDef(0, 100)
    col_neg_pos = ColumnDef(-10, 10)
    df = mock_data({"col_0_100": col_0_100, "col_neg_pos": col_neg_pos})

    assert df.select(pl.len()).item() == 1000
    assert 0 < df.get_column("col_0_100")[0] < 2
    assert 98 < df.get_column("col_0_100")[999] < 100
    assert (
        df.get_column("col_neg_pos")[0] + df.get_column("col_neg_pos")[999]
    ) == approx(0)
