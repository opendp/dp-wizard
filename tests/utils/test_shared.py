from dp_wizard.utils.shared import df_to_columns
import polars as pl


def test_two_column_df_to_columns():
    df = pl.DataFrame(
        {
            "bin": ["(-inf, 5]", "(10, 20]", "(5, 10]"],
            "len": [0, 20, 10],
        }
    )
    assert df_to_columns(df) == (
        ("(-inf, 5]", "(5, 10]", "(10, 20]"),
        (0, 10, 20),
    )


def test_three_column_string_df_to_columns():
    df = pl.DataFrame(
        {
            "bin": ["(0, 1]", "(1, 2]", "(0, 1]", "(1, 2]"],
            "str": ["A", "A", "B", "B"],
            "len": [0, 10, 20, 30],
        }
    )
    assert df_to_columns(df) == (
        ("(0, 1] A", "(0, 1] B", "(1, 2] A", "(1, 2] B"),
        (0, 20, 10, 30),
    )


def test_three_column_numeric_df_to_columns():
    df = pl.DataFrame(
        {
            "bin": ["(0, 1]", "(1, 2]", "(0, 1]", "(1, 2]"],
            "num": [1, 1, 2, 2],
            "len": [0, 10, 20, 30],
        }
    )
    assert df_to_columns(df) == (
        ("(0, 1] 1", "(0, 1] 2", "(1, 2] 1", "(1, 2] 2"),
        (0, 20, 10, 30),
    )


def test_no_rows_df_to_columns():
    df = pl.DataFrame(
        {
            "bin": [],
            "num": [],
            "len": [],
        }
    )
    assert df_to_columns(df) == (
        tuple(),
        tuple(),
    )
