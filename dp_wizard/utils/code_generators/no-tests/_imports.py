import polars as pl
import opendp.prelude as dp
import matplotlib.pyplot as plt

# The OpenDP Library team is working to vet the core algorithms.
# Until that is complete we need to opt-in to use these features.
dp.enable_features("contrib")
