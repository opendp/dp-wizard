# # OpenDP Demo
#
# This is a demonstration of how OpenDP can be used to create
# a differentially private release. To learn more about what's
# going on here, see the documentation for OpenDP: https://docs.opendp.org/
#
# First install and import the required dependencies:

# +
# %pip install DEPENDENCIES
# -

# +
IMPORTS_BLOCK
# -

# Then define some utility functions to handle dataframes and plot results:

# +
UTILS_BLOCK
# -

# Based on the input you provided, for each column we'll create a set of cut points,
# and a Polars expression that describes how we want to summarize that column.

# +
COLUMNS_BLOCK
# -

# Next, we'll define our Context. This is where we set the privacy budget,
# and set the weight for each query under that overall budget.

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

# If we try to run more queries at this point, it will error. Once the privacy budget
# is consumed, the library prevents you from running more queries with that Queryable.

# # Coda
# The code below produces a summary report.

# +
REPORTS_BLOCK
# -
