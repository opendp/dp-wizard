# See the OpenDP Library docs for more on making private means:
# https://docs.opendp.org/en/OPENDP_V_VERSION/getting-started/tabular-data/essential-statistics.html#Mean

EXPR_NAME = pl.col(COLUMN_NAME).cast(float).dp.mean((LOWER_BOUND, UPPER_BOUND))
