# See the OpenDP docs for more on making private counts:
# https://docs.opendp.org/en/stable/getting-started/tabular-data/essential-statistics.html#Count

EXPR_NAME = (
    pl.col(COLUMN_NAME)
    .cast(float)
    .fill_nan(0)
    .fill_null(0)
    .dp.clamp(LOWER_BOUND, UPPER_BOUND)
    .dp.len()
)
