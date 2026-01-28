# # TITLE
#
# CUSTOM_NOTE

# + [markdown] tags=["Full_Tutorial"]
# Jump ahead:
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

# + [markdown] tags=["Full_Tutorial"]
# ### Context
#
# Next, we'll define our Context. This is where we set the privacy budget,
# and the columns that will be part of the synthetic dataset.

# + tags=["Full_Tutorial"]
SYNTH_CONTEXT_BLOCK
# -

# + [markdown] tags=["Full_Tutorial"]
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

# + [markdown] tags=["Full_Tutorial"]
# If we try to run more queries at this point, it will error. Once the privacy budget
# is consumed, the library prevents you from running any more queries.
# -

# + [markdown] tags=["Postprocessing"]
# ## Postprocessing
# This code produces the other files that are part of the package.
# -

# + tags=["Postprocessing"]
SYNTH_REPORTS_BLOCK
# -
