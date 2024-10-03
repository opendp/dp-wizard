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


def analysis_server(input, output, session):
    @render.plot()
    def plot_preview():
        col_0_100 = ColumnDef(0, 100)
        col_neg_pos = ColumnDef(-10, 10)
        df = mock_data({"col_0_100": col_0_100}, row_count=20)

        # plot
        figure, axes = plt.subplots()
        figure.set_size_inches(4, 2)

        # make data:
        y = df["col_0_100"].to_list()
        x = 0.5 + np.arange(len(y))
        axes.bar(
            x, y, width=0.8, edgecolor="skyblue", linewidth=1, yerr=2, color="skyblue"
        )
        axes.bar(
            x[:5],
            y[:5],
            width=0.8,
            edgecolor="skyblue",
            linewidth=0.5,
            yerr=2,
            color="white",
        )
        axes.hlines([10], 0, 20, colors=["black"], linestyles=["dotted"])

        axes.set(xlim=(0, 20), ylim=(0, 100))
        axes.get_xaxis().set_ticks([0, 20])
        axes.get_yaxis().set_ticks([])

        return figure

    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")
