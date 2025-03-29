CONFIG_NAME = (
    pl.col(COLUMN_NAME)
    .cast(float)
    .fill_nan(0)
    .fill_null(0)
    .dp.quantile(0.5, make_cut_points(LOWER_BOUND, UPPER_BOUND, bin_count=100))
    # todo: Get the bin count from the user?
    # or get nice round numbers?
    # See: https://github.com/opendp/opendp/issues/1706
)
