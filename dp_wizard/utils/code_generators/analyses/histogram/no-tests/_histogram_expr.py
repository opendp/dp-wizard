# See the OpenDP Library docs for more on making private histograms:
# https://docs.opendp.org/en/stable/getting-started/examples/histograms.html

# Use the public information to make cut points for COLUMN_NAME:
CUT_LIST_NAME = make_cut_points(
    lower_bound=LOWER_BOUND,
    upper_bound=UPPER_BOUND,
    bin_count=BIN_COUNT,
)

# Use these cut points to add a new binned column to the table:
BIN_EXPR_NAME = (
    pl.col(COLUMN_NAME)
    .cut(CUT_LIST_NAME)
    .alias(BIN_COLUMN_NAME)  # Give the new column a name.
    .cast(pl.String)
)
