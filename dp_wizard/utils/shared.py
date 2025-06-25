# These functions are used both in the application
# and in generated notebooks.
import polars as pl


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


def merge_columns(df: pl.DataFrame):
    """
    Merge all but the last column of a dataframe and sort.
    >>> df = pl.DataFrame(data={
    ...     'bin': ['(0, 5]', '(5, 10]', '(10, 15]'],
    ...     'spin': ['up', 'down', 'up'],
    ...     'value': [1, 2, 3]
    ... })
    >>> merge_columns(df)
    shape: (3, 2)
    ┌──────────────┬───────┐
    │ group        ┆ value │
    │ ---          ┆ ---   │
    │ str          ┆ i64   │
    ╞══════════════╪═══════╡
    │ (0, 5] up    ┆ 1     │
    │ (5, 10] down ┆ 2     │
    │ (10, 15] up  ┆ 3     │
    └──────────────┴───────┘
    """
    merged_key_rows = [
        (" ".join(str(k) for k in keys), value) for (*keys, value) in df.rows()
    ]
    sorted_rows = sorted(merged_key_rows, key=lambda row: interval_bottom(row[0]))
    groups, counts = zip(*sorted_rows)
    return pl.DataFrame(data={"group": groups, "count": counts})


def plot_bars(
    df: pl.DataFrame, error: float, cutoff: float, title: str
):  # pragma: no cover
    """
    Given a Dataframe, make a bar plot of the data in the last column,
    with labels from the prior columns.
    """
    import plotly.express as px

    merged_df = merge_columns(df)
    fig = px.bar(merged_df, x="group", y="count", title=title)
    fig.show()
