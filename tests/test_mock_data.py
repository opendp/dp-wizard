import polars as pl

from dp_creator_ii.utils.mock_data import mock_data, ColumnDef


def test_mock_data():
    col_0_100 = ColumnDef(0, 100)
    col_neg_pos = ColumnDef(-10, 10)
    df = mock_data({"col_0_100": col_0_100, "col_neg_pos": col_neg_pos})

    assert df.select(pl.len()).item() == 1000

    # Smallest value is slightly above the lower bound,
    # so we don't get one isolated value in the lowest bin.
    assert 0 < df.get_column("col_0_100")[0] < 1
    assert -10 < df.get_column("col_neg_pos")[0] < -9

    assert df.get_column("col_0_100")[999] == 100
    assert df.get_column("col_neg_pos")[999] == 10
