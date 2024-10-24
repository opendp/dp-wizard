import matplotlib.pyplot as plt


def _df_to_columns(df):
    """
    >>> import polars as pl
    >>> df = pl.DataFrame({
    ...     "bin": ["A", "B", "C"],
    ...     "len": [0, 10, 20],
    ... })
    >>> _df_to_columns(df)
    (['A', 'B', 'C'], [0, 10, 20])
    """
    return tuple(list(df[col]) for col in df.columns)


def plot_histogram(histogram_df, error, cutoff):  # pragma: no cover
    labels, values = _df_to_columns(histogram_df)
    _figure, axes = plt.subplots()
    bar_colors = ["blue" if v > cutoff else "lightblue" for v in values]
    axes.bar(labels, values, color=bar_colors, yerr=error)
    axes.axhline(cutoff, color="lightgrey", zorder=-1)
    # TODO: Since this seems to return None, how does the information flow?
