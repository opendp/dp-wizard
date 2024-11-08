import polars as pl
import opendp.prelude as dp

# The OpenDP team is working to vet the core algorithms.
# Until that is complete we need to opt-in to use these features.
dp.enable_features("contrib")


def make_cut_points(lower_bound, upper_bound, bin_count):
    """
    Returns one more cut point than the bin_count.
    (There are actually two more bins, extending to
    -inf and +inf, but we'll ignore those.)
    Cut points are evenly spaced from lower_bound to upper_bound.
    """
    bin_width = (upper_bound - lower_bound) / bin_count
    return [round(lower_bound + i * bin_width, 2) for i in range(bin_count + 1)]
