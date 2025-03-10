# From the public information, determine the bins for COLUMN_NAME:
CUT_LIST_NAME = make_cut_points(
    lower_bound=LOWER_BOUND,
    upper_bound=UPPER_BOUND,
    bin_count=BIN_COUNT,
)

# Use these bins to define a Polars column:
CONFIG_NAME = (
    pl.col(COLUMN_NAME)
    .cut(CUT_LIST_NAME)
    .alias(BIN_COLUMN_NAME)  # Give the new column a name.
    .cast(pl.String)
)
