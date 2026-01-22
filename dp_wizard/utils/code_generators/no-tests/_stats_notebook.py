# # TITLE
#
# CUSTOM_NOTE

# + [markdown] tags=["Full_Tutorial"]
# Jump ahead:
# - [Analysis](#Analysis)
# - [Results](#Results)
#
# ## Prerequisites
#
# First install and import the required dependencies:
# WINDOWS_COMMENT_BLOCK
# -

# + tags=["Full_Tutorial"]
# %pip install DEPENDENCIES
# -

# + tags=["Full_Tutorial"]
IMPORTS_BLOCK
# -

# + [markdown] tags=["Full_Tutorial"]
# Then define some utility functions to handle dataframes and plot results:
# -

# + tags=["Full_Tutorial"]
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
STATS_CONTEXT_BLOCK
# -

# CSV_COMMENT_BLOCK
#
# ## Results
#
# Finally, we run the queries and plot the results.

STATS_QUERIES_BLOCK

# + [markdown] tags=["Full_Tutorial"]
# If we try to run more queries at this point, it will error. Once the privacy budget
# is consumed, the library prevents you from running any more queries.
# -

# + [markdown] tags=["Postprocessing"]
# ## Postprocessing
# This code produces the other files that are part of the package.
# -

# + tags=["Postprocessing"]
STATS_REPORTS_BLOCK
# -
