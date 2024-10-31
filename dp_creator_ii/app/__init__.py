from pathlib import Path
import logging

from shiny import App, ui, reactive

from dp_creator_ii.utils.argparse_helpers import get_csv_contrib_from_cli
from dp_creator_ii.app import analysis_panel, dataset_panel, results_panel


logging.basicConfig(level=logging.INFO)

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
    (csv_path_from_cli, contributions_from_cli, is_demo) = get_csv_contrib_from_cli()
    csv_path = reactive.value(csv_path_from_cli)
    contributions = reactive.value(contributions_from_cli)

    dataset_panel.dataset_server(
        input,
        output,
        session,
        csv_path=csv_path,
        contributions=contributions,
        is_demo=is_demo,
    )
    analysis_panel.analysis_server(
        input,
        output,
        session,
        csv_path=csv_path,
        contributions=contributions,
        is_demo=is_demo,
    )
    results_panel.results_server(input, output, session)
    session.on_ended(ctrl_c_reminder)


app = App(app_ui, server)
