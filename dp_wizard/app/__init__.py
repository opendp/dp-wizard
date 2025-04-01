from pathlib import Path

from shiny import App, ui, reactive, Inputs, Outputs, Session

from dp_wizard.utils.argparse_helpers import get_cli_info, CLIInfo
from dp_wizard.app import (
    about_panel,
    analysis_panel,
    dataset_panel,
    results_panel,
    feedback_panel,
)


app_ui = ui.page_bootstrap(
    ui.head_content(ui.include_css(Path(__file__).parent / "css" / "styles.css")),
    ui.navset_tab(
        about_panel.about_ui(),
        dataset_panel.dataset_ui(),
        analysis_panel.analysis_ui(),
        results_panel.results_ui(),
        feedback_panel.feedback_ui(),
        selected=dataset_panel.dataset_panel_id,
        id="top_level_nav",
    ),
    title="DP Wizard",
)


def ctrl_c_reminder():  # pragma: no cover
    print("Session ended (Press CTRL+C to quit)")


def make_server_from_cli_info(cli_info: CLIInfo):
    def server(input: Inputs, output: Outputs, session: Session):  # pragma: no cover
        public_csv_path = reactive.value(cli_info.public_csv_path or "")
        private_csv_path = reactive.value(cli_info.private_csv_path or "")

        contributions = reactive.value(cli_info.contributions)

        analysis_types = reactive.value({})
        lower_bounds = reactive.value({})
        upper_bounds = reactive.value({})
        bin_counts = reactive.value({})
        groups = reactive.value([])
        weights = reactive.value({})
        epsilon = reactive.value(1.0)

        about_panel.about_server(
            input,
            output,
            session,
        )
        dataset_panel.dataset_server(
            input,
            output,
            session,
            cli_info=cli_info,
            public_csv_path=public_csv_path,
            private_csv_path=private_csv_path,
            contributions=contributions,
        )
        analysis_panel.analysis_server(
            input,
            output,
            session,
            is_demo=cli_info.is_demo,
            public_csv_path=public_csv_path,
            private_csv_path=private_csv_path,
            contributions=contributions,
            analysis_types=analysis_types,
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds,
            bin_counts=bin_counts,
            groups=groups,
            weights=weights,
            epsilon=epsilon,
        )
        results_panel.results_server(
            input,
            output,
            session,
            public_csv_path=public_csv_path,
            private_csv_path=private_csv_path,
            contributions=contributions,
            analysis_types=analysis_types,
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds,
            bin_counts=bin_counts,
            groups=groups,
            weights=weights,
            epsilon=epsilon,
        )
        feedback_panel.feedback_server(
            input,
            output,
            session,
        )
        session.on_ended(ctrl_c_reminder)

    return server


app = App(app_ui, make_server_from_cli_info(get_cli_info()))
