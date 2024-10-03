from shiny import ui, reactive, render
import matplotlib.pyplot as plt
import numpy as np

from dp_creator_ii.mock_data import mock_data, ColumnDef


def analysis_ui():
    return ui.nav_panel(
        "Define Analysis",
        "TODO: Define analysis",
        ui.output_plot("plot_preview"),
        "(This plot is only to demonstrate that plotting works.)",
        ui.input_action_button("go_to_results", "Download results"),
        value="analysis_panel",
    )


def plot(y_values, x_min_label="min", x_max_label="max", y_cutoff=0):
    figure, axes = plt.subplots()
    # figure.set_size_inches(4, 2)

    x_values = 0.5 + np.arange(len(y_values))
    axes.bar(
        x_values,
        y_values,
        width=0.8,
        edgecolor="skyblue",
        linewidth=1,
        yerr=2,
        color="skyblue",
    )
    axes.bar(
        x_values[:5],
        y_values[:5],
        width=0.8,
        edgecolor="skyblue",
        linewidth=0.5,
        yerr=2,
        color="white",
    )
    axes.hlines([y_cutoff], 0, len(y_values), colors=["black"], linestyles=["dotted"])

    axes.set(xlim=(0, len(y_values)), ylim=(0, max(y_values)))
    axes.get_xaxis().set_ticks([])
    axes.get_yaxis().set_ticks([])

    return figure


def analysis_server(input, output, session):
    @render.plot()
    def plot_preview():
        df = mock_data({"col_0_100": ColumnDef(0, 100)}, row_count=20)

        return plot(df["col_0_100"].to_list(), y_cutoff=10)

    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")
