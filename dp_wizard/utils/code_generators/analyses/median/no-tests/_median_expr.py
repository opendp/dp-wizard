# See the OpenDP Library docs for more on making private medians and quantiles:
# https://docs.opendp.org/en/OPENDP_VERSION/getting-started/tabular-data/essential-statistics.html#Median

EXPR_NAME = (
    pl.col(COLUMN_NAME)
    .cast(float)
    .fill_nan(0)
    .fill_null(0)
    .dp.quantile(0.5, make_cut_points(LOWER_BOUND, UPPER_BOUND, bin_count=BIN_COUNT))
    # Or use "dp.median" which provides 0.5 implicitly.
)
