# These functions are used both in the application and in generated notebooks.
from polars import DataFrame


def make_cut_points(lower_bound: float, upper_bound: float, bin_count: int):
    """
    Returns one more cut point than the bin_count.
    (There are actually two more bins, extending to
    -inf and +inf, but we'll ignore those.)
    Cut points are evenly spaced from lower_bound to upper_bound.
    >>> make_cut_points(0, 10, 2)
    [0.0, 5.0, 10.0]
    """
    bin_width = (upper_bound - lower_bound) / bin_count
    return [round(lower_bound + i * bin_width, 2) for i in range(bin_count + 1)]


def interval_bottom(interval: str):
    """
    >>> interval_bottom("(10, 20]")
    10.0
    """
    return float(interval.split(",")[0][1:])


def df_to_columns(df: DataFrame):
    """
    Transform a Dataframe into a format that is easier to plot,
    parsing the interval strings to sort them as numbers.
    >>> import polars as pl
    >>> df = pl.DataFrame({
    ...     "bin": ["(-inf, 5]", "(10, 20]", "(5, 10]"],
    ...     "len": [0, 20, 10],
    ... })
    >>> df_to_columns(df)
    (('(-inf, 5]', '(5, 10]', '(10, 20]'), (0, 10, 20))
    """
    sorted_rows = sorted(df.rows(), key=lambda pair: interval_bottom(pair[0]))
    return tuple(zip(*sorted_rows))


def plot_histogram(
    histogram_df: DataFrame, error: float, cutoff: float
):  # pragma: no cover
    """
    Given a Dataframe for a histogram, plot the data.
    """
    import matplotlib.pyplot as plt

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
