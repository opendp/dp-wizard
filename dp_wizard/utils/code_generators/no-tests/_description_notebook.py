# # TITLE
#
# CUSTOM_NOTE
#
# Jump ahead:
# - [Analysis](#Analysis)
# - [Results](#Results)
#
# ## Prerequisites
#
# First install and import the required dependencies:
# WINDOWS_COMMENT_BLOCK

# +
# %pip install DEPENDENCIES
# -

# +
IMPORTS_BLOCK
# -

# ## Analysis
#
# For each column numeric column we'll create a Polars expression
# for a histogram that spans orders of magnitude.

DESCRIPTION_COLUMNS_BLOCK

# ### Context
#
# Next, we'll define our Context. This is where we set the privacy budget,
# and set the weight for each query under that overall budget.

# +
DESCRIPTION_CONTEXT_BLOCK
# -

# ENCODING_COMMENT_BLOCK
#
# ## Results
#
# Finally, we run the queries.

DESCRIPTION_QUERIES_BLOCK

# If we try to run more queries at this point, it will error. Once the privacy budget
# is consumed, the library prevents you from running any more queries.

# # Coda
# The code below produces a summary report.

# +
REPORTS_BLOCK
# -
