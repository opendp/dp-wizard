from pathlib import Path
import logging

from shiny import App, ui, reactive

from dp_creator_ii.utils.argparse_helpers import get_cli_info
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


def make_server_from_cli_info(cli_info):
    def server(input, output, session):  # pragma: no cover
        csv_path = reactive.value(cli_info.csv_path)
        contributions = reactive.value(cli_info.contributions)

        dataset_panel.dataset_server(
            input,
            output,
            session,
            csv_path=csv_path,
            contributions=contributions,
            is_demo=cli_info.is_demo,
        )
        analysis_panel.analysis_server(
            input,
            output,
            session,
            csv_path=csv_path,
            contributions=contributions,
            is_demo=cli_info.is_demo,
        )
        results_panel.results_server(input, output, session)
        session.on_ended(ctrl_c_reminder)

    return server


app = App(app_ui, make_server_from_cli_info(get_cli_info()))
