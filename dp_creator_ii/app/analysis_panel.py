from shiny import ui, reactive, render

from dp_creator_ii.mock_data import mock_data, ColumnDef
from dp_creator_ii.app.plots import plot_error_bars_with_cutoff


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
        min_x = 0
        max_x = 100
        df = mock_data({"col_0_100": ColumnDef(min_x, max_x)}, row_count=20)
        return plot_error_bars_with_cutoff(
            df["col_0_100"].to_list(),
            x_min_label=min_x,
            x_max_label=max_x,
            y_cutoff=30,
            y_error=5,
        )

    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")
