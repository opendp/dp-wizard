import matplotlib.pyplot as plt
import numpy as np


def plot_error_bars_with_cutoff(
    y_values, x_min_label="min", x_max_label="max", y_cutoff=0, y_error=0
):
    x_values = 0.5 + np.arange(len(y_values))
    x_values_above = []
    x_values_below = []
    y_values_above = []
    y_values_below = []
    for x, y in zip(x_values, y_values):
        if y < y_cutoff:
            x_values_below.append(x)
            y_values_below.append(y)
        else:
            x_values_above.append(x)
            y_values_above.append(y)

    figure, axes = plt.subplots()
    color = "skyblue"
    shared = {
        "width": 0.8,
        "edgecolor": color,
        "linewidth": 1,
        "yerr": y_error,
    }
    axes.bar(x_values_above, y_values_above, color=color, **shared)
    axes.bar(x_values_below, y_values_below, color="white", **shared)
    axes.hlines([y_cutoff], 0, len(y_values), colors=["black"], linestyles=["dotted"])

    axes.set(xlim=(0, len(y_values)), ylim=(0, max(y_values)))
    axes.get_xaxis().set_ticks(
        ticks=[x_values[0], x_values[-1]],
        labels=[x_min_label, x_max_label],
    )
    axes.get_yaxis().set_ticks([])

    return figure
