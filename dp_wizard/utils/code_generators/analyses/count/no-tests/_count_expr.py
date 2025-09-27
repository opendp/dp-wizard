# See the OpenDP docs for more on making private counts:
# https://docs.opendp.org/en/OPENDP_V_VERSION/getting-started/tabular-data/essential-statistics.html#Count

EXPR_NAME = pl.col(COLUMN_NAME).cast(float).dp.count().alias("count")
