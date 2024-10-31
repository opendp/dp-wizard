# From the public information, determine the bins:
CUT_LIST_NAME = make_cut_points(MIN, MAX, BINS)

# Use these bins to define a Polars column:
POLARS_CONFIG_NAME = (
    pl.col(COLUMN_NAME)
    .cut(CUT_LIST_NAME)
    .alias(BIN_COLUMN_NAME)  # Give the new column a name.
    .cast(pl.String)
)
