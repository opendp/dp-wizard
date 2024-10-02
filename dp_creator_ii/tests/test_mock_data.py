from dp_creator_ii.mock_data import mock_data, ColumnDef


def test_mock_data():
    col_0_100 = ColumnDef(0, 100)
    col_neg_pos = ColumnDef(-10, 10)
    df = mock_data({"col_0_100": col_0_100, "col_neg_pos": col_neg_pos}, row_count=5)
    print(df)
    assert df == None
