# These functions are used both in the application
# and in generated notebooks.
from polars import DataFrame


def interval_bottom(interval: str) -> float:
    """
    >>> interval_bottom("(10, 20]")
    10.0
    >>> interval_bottom("-10")
    -10.0
    >>> interval_bottom("unexpected")
    0.0
    """
    # Intervals from Polars default to open on the left,
    # so that's the only case we cover with replace().
    try:
        return float(interval.split(",")[0].replace("(", ""))
    except ValueError:
        return 0.0


delim = "; "
first = lambda merged: merged.split(delim)[0]  # noqa: E731


def df_to_columns(df: DataFrame):
    """
    Transform a Dataframe into a format that is easier to plot,
    parsing the interval strings to sort them as numbers.
    """
    merged_key_rows = [
        (delim.join(str(k) for k in keys), value) for (*keys, value) in df.rows()
    ]
    sorted_rows = sorted(merged_key_rows, key=lambda row: interval_bottom(row[0]))
    transposed = tuple(zip(*sorted_rows))
    return transposed if transposed else (tuple(), tuple())


def plot_bars(df: DataFrame, title: str, error: float = 0):  # pragma: no cover
    """
    Given a Dataframe, make a bar plot of the data in the last column,
    with labels from the prior columns.
    """
    import matplotlib.pyplot as plt

    plt.rcParams["figure.figsize"] = (12, 4)

    bins, values = df_to_columns(df)
    _figure, axes = plt.subplots()
    top_bins = list({first(b) for b in bins})
    cmap = plt.cm.tab10  # pyright: ignore[reportAttributeAccessIssue]
    bar_colors = [cmap(top_bins.index(first(b)) % cmap.N) for b in bins]
    axes.bar(bins, values, color=bar_colors, yerr=error)
    axes.set_xticks(bins, bins, rotation=45)
    axes.set_ylim(bottom=0)
    axes.set_title(title)
