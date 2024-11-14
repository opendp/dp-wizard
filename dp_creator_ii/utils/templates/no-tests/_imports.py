import polars as pl
import opendp.prelude as dp
import matplotlib.pyplot as plt

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


def df_to_columns(df):
    """
    >>> import polars as pl
    >>> df = pl.DataFrame({
    ...     "bin": ["A", "B", "C"],
    ...     "len": [0, 10, 20],
    ... })
    >>> df_to_columns(df)
    (['A', 'B', 'C'], [0, 10, 20])
    """
    return tuple(list(df[col]) for col in df.columns)


def plot_histogram(histogram_df, error, cutoff):  # pragma: no cover
    bins, values = df_to_columns(histogram_df)
    mod = (len(bins) // 12) + 1
    majors = [label for i, label in enumerate(bins) if i % mod == 0]
    minors = [label for i, label in enumerate(bins) if i % mod != 0]
    _figure, axes = plt.subplots()
    bar_colors = ["blue" if v > cutoff else "lightblue" for v in values]
    axes.bar(bins, values, color=bar_colors, yerr=error)
    axes.set_xticks(majors, majors)
    axes.set_xticks(minors, ["" for _ in minors], minor=True)
    axes.axhline(cutoff, color="lightgrey", zorder=-1)
    axes.set_ylim(bottom=0)
