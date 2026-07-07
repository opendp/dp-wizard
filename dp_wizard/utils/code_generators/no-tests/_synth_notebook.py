# {"tagmap":{
#   "Brief Report": [],
#   "Full Tutorial": ["tutorial"],
#   "Include Postprocessing": ["tutorial", "postprocessing"]
# }}

# # TITLE
#
# CUSTOM_NOTE

# + [markdown] tags=["tutorial"]
# Jump ahead:
# - [Results](#Results)
#
# ## Prerequisites
#
# First install and import the required dependencies:
# WINDOWS_COMMENT_BLOCK
# -

# + tags=["tutorial"]
# %pip install DEPENDENCIES
# -

# + tags=["tutorial"]
IMPORTS_BLOCK
# -

# + [markdown] tags=["tutorial"]
# Then define some utility functions to handle dataframes and plot results:
# -

# + tags=["tutorial"]
UTILS_BLOCK
# -

# + [markdown] tags=["tutorial"]
# ### Context
#
# Next, we'll define our Context. This is where we set the privacy budget,
# and the columns that will be part of the synthetic dataset.

# + tags=["tutorial"]
SYNTH_CONTEXT_BLOCK
# -

# + [markdown] tags=["tutorial"]
# CSV_COMMENT_BLOCK
# -

# ## Results
#
# First, we'll release a contingency table, a data structure which can give us
# DP counts for different combinations of column values.

SYNTH_QUERY_BLOCK

# If there are lots of null values, it may mean that the OpenDP library was not able to
# collect enough information to describe your dataset within the privacy budget.
# You might try:
# - Increasing your privacy budget
# - Selecting fewer columns
# - Selecting fewer cutpoints
# - Filling in the "keys" kwarg
# - Preprocessing to combine keys which occur a small number of times

# + [markdown] tags=["tutorial"]
# If we try to run more queries at this point, it will error. Once the privacy budget
# is consumed, the library prevents you from running any more queries.
# -

# + [markdown] tags=["postprocessing"]
# ## Postprocessing
# This code produces the other files that are part of the package.
# -

# + tags=["postprocessing"]
SYNTH_REPORTS_BLOCK
# -
