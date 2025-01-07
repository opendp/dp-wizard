# This is a demonstration of how OpenDP can be used to create
# a differentially private release. To learn more about what's
# going on here, see the documentation for OpenDP: https://docs.opendp.org/
#
# First install the required dependencies:

# +
# %pip install DEPENDENCIES
# -

# +
IMPORTS_BLOCK
# -

# Based on the input you provided, for each column we'll create a set of cut points,
# and a Polars expression that describes how we want to summarize that column.

# +
COLUMNS_BLOCK
# -

# Next, we'll define our Context. This is where we set the privacy budget,
# and set the weight for each query under that overall budget.
# If we try to run more one more query than we have weights, it will error.
# Once the privacy budget is consumed, you shouldn't run more queries.

# +
CONTEXT_BLOCK
# -

# A note on `utf8-lossy`: CSVs can use different "character encodings" to
# represent characters outside the plain ascii character set, but out of the box
# the Polars library only supports UTF8. Specifying `utf8-lossy` preserves as
# much information as possible, and any unrecognized characters will be replaced
# by "�". If this is not sufficient, you will need to preprocess your data to
# reencode it as UTF8.
#
# Finally, we run the queries and plot the results.

QUERIES_BLOCK

# # Coda
# The code below produces a summary report.

# +
REPORTS_BLOCK
# -
