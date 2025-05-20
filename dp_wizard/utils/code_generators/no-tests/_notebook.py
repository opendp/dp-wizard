# # TITLE
#
# This is a demonstration of how the [OpenDP Library](https://docs.opendp.org/)
# can be used to create a differentially private release.
#
# ## Prerequisites
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

# ## Analysis
#
# Based on the input you provided, for each column we'll create a Polars expression
# that describes how we want to summarize that column.

COLUMNS_BLOCK

# ### Context
#
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
# ## Results
#
# Finally, we run the queries and plot the results.

QUERIES_BLOCK

# If we try to run more queries at this point, it will error. Once the privacy budget
# is consumed, the library prevents you from running any more queries.

# # Coda
# The code below produces a summary report.

# +
REPORTS_BLOCK
# -
