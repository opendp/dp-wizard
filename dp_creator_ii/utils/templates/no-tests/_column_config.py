# From the public information, determine the bins:
BINS_LIST_NAME = list(
    range(
        MIN,
        MAX,
        int((MAX - MIN + 1) / BINS),
    )
)

# Use these bins to define a Polars column:
POLARS_CONFIG_NAME = (
    pl.col(COLUMN_NAME)
    .cut(BINS_LIST_NAME)
    .alias(BIN_COLUMN_NAME)  # Give the new column a name.
    .cast(pl.String)
)
