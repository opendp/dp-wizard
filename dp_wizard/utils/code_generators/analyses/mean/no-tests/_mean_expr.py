# See the OpenDP Library docs for more on making private means:
# https://docs.opendp.org/en/stable/getting-started/tabular-data/essential-statistics.html#Mean

EXPR_NAME = pl.col(COLUMN_NAME).dp.mean((LOWER_BOUND, UPPER_BOUND))
