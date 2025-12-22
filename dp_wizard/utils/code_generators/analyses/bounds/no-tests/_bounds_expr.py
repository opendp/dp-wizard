# See the OpenDP Library docs for more on making private histograms:
# https://docs.opendp.org/en/OPENDP_V_VERSION/getting-started/examples/histograms.html

# Use the public information to make cut points for COLUMN_NAME:
CUT_LIST_NAME = make_exponential_cut_points(
    extreme=EXTREME,
)

# Use these cut points to add a new binned column to the table:
BIN_EXPR_NAME = (
    pl.col(COLUMN_NAME)
    .cut(CUT_LIST_NAME)  # Use "left_closed=True" to switch endpoint inclusion.
    .alias(BIN_COLUMN_NAME)  # Give the new column a name.
    .cast(pl.String)
)
