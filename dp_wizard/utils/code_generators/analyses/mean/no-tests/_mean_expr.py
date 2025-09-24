# See the OpenDP Library docs for more on making private means:
# https://docs.opendp.org/en/OPENDP_VERSION/getting-started/tabular-data/essential-statistics.html#mean
#
# Note: While this is fine for taking one DP mean, it does spend some of
# your privacy budget each time to calculate the number of records:
# It is better to do that explicitly, and then collect DP sums for
# each column of interest.

EXPR_NAME = (
    pl.col(COLUMN_NAME)
    .cast(float)
    .fill_nan(0)
    .fill_null(0)
    .dp.mean((LOWER_BOUND, UPPER_BOUND))
)
