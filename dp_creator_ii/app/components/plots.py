import matplotlib.pyplot as plt


def _df_to_dict(df):  # pragma: no cover
    # TODO: Add doctest
    return {
        # The name of the key will vary, so just get the first value.
        list(range_len.values())[0]: range_len["len"]
        for range_len in df.to_dicts()
    }


def plot_histogram(histogram_df, error, cutoff):  # pragma: no cover
    histogram_dict = _df_to_dict(histogram_df)
    labels, values = zip(*histogram_dict.items())
    _figure, axes = plt.subplots()
    bar_colors = ["blue" if v > cutoff else "lightblue" for v in values]
    axes.bar(labels, values, color=bar_colors, yerr=error)
    axes.axhline(cutoff, color="lightgrey", zorder=-1)
