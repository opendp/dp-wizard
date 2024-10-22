from pathlib import Path

from shiny import App, ui

from dp_creator_ii.app import analysis_panel, dataset_panel, results_panel


app_ui = ui.page_bootstrap(
    ui.head_content(ui.include_css(Path(__file__).parent / "css" / "styles.css")),
    ui.navset_tab(
        dataset_panel.dataset_ui(),
        analysis_panel.analysis_ui(),
        results_panel.results_ui(),
        id="top_level_nav",
    ),
    title="DP Creator II",
)


def ctrl_c_reminder():  # pragma: no cover
    print("Session ended (Press CTRL+C to quit)")


def server(input, output, session):  # pragma: no cover
    dataset_panel.dataset_server(input, output, session)
    analysis_panel.analysis_server(input, output, session)
    results_panel.results_server(input, output, session)
    session.on_ended(ctrl_c_reminder)


app = App(app_ui, server)
