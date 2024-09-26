from shiny import App, ui

from dp_creator_ii.app import analysis_panel, dataset_panel, results_panel


app_ui = ui.page_bootstrap(
    ui.navset_tab(
        dataset_panel.dataset_ui(),
        analysis_panel.analysis_ui(),
        results_panel.results_ui(),
        id="top_level_nav",
    ),
    title="DP Creator II",
)


def server(input, output, session):
    dataset_panel.dataset_server(input, output, session)
    analysis_panel.analysis_server(input, output, session)
    results_panel.results_server(input, output, session)


app = App(app_ui, server)
