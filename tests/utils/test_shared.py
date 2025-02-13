from dp_wizard.utils.shared import df_to_columns
import polars as pl


def test_2_df_to_columns():
    df_2 = pl.DataFrame(
        {
            "bin": ["(-inf, 5]", "(10, 20]", "(5, 10]"],
            "len": [0, 20, 10],
        }
    )
    assert df_to_columns(df_2) == (
        ("(-inf, 5]", "(5, 10]", "(10, 20]"),
        (0, 10, 20),
    )


def test_3_df_to_columns():
    df_3 = pl.DataFrame(
        {
            "bin": ["(0, 1]", "(1, 2]", "(0, 1]", "(1, 2]"],
            "etc": ["A", "A", "B", "B"],
            "len": [0, 10, 20, 30],
        }
    )
    assert df_to_columns(df_3) == (
        ("(0, 1] A", "(0, 1] B", "(1, 2] A", "(1, 2] B"),
        (0, 20, 10, 30),
    )
