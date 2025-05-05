# These functions are used both in the application
# and in generated notebooks.
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
    >>> interval_bottom("-10")
    -10.0
    >>> interval_bottom("unexpected")
    0.0
    """
    # Intervals from Polars are always open on the left,
    # so that's the only case we cover with replace().
    try:
        return float(interval.split(",")[0].replace("(", ""))
    except ValueError:
        return 0.0


def df_to_columns(df: DataFrame):
    """
    Transform a Dataframe into a format that is easier to plot,
    parsing the interval strings to sort them as numbers.
    """
    merged_key_rows = [
        (" ".join(str(k) for k in keys), value) for (*keys, value) in df.rows()
    ]
    sorted_rows = sorted(merged_key_rows, key=lambda row: interval_bottom(row[0]))
    transposed = tuple(zip(*sorted_rows))
    return transposed if transposed else (tuple(), tuple())


def plot_bars(
    df: DataFrame, error: float, cutoff: float, title: str
):  # pragma: no cover
    """
    Given a Dataframe, make a bar plot of the data in the last column,
    with labels from the prior columns.
    """
    import matplotlib.pyplot as plt

    plt.rcParams["figure.figsize"] = (12, 4)

    bins, values = df_to_columns(df)
    _figure, axes = plt.subplots()
    bar_colors = ["blue" if v > cutoff else "lightblue" for v in values]
    axes.bar(bins, values, color=bar_colors, yerr=error)
    axes.set_xticks(bins, bins, rotation=45)
    axes.axhline(cutoff, color="lightgrey", zorder=-1)
    axes.set_ylim(bottom=0)
    axes.set_title(title)
