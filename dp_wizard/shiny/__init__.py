from pathlib import Path

from htmltools import Tag
from shiny import App, Inputs, Outputs, Session, reactive, ui

from dp_wizard import package_root
from dp_wizard.shiny.components.icons import tutorial_icon
from dp_wizard.shiny.panels import (
    about_panel,
    analysis_panel,
    dataset_panel,
    results_panel,
)
from dp_wizard.types import AppState, Product
from dp_wizard.utils import config
from dp_wizard.utils.argparse_helpers import CLIInfo
from dp_wizard.utils.csv_helper import (
    CsvInfo,
    make_sample_csv,
)

_shiny_root = package_root / "shiny"
_assets_root = _shiny_root / "assets"
assert _assets_root.exists()


def make_app(cli_info: CLIInfo) -> App:
    return App(
        _make_app_ui(cli_info),
        _make_server(cli_info),
        static_assets=_assets_root,
    )


def _get_is_tutorial_mode(cli_info: CLIInfo) -> bool:
    is_tutorial_mode = config.get_is_tutorial_mode()
    if is_tutorial_mode is None:
        is_tutorial_mode = cli_info.get_is_tutorial_mode()  # pragma: no cover
    return is_tutorial_mode


def _get_is_dark_mode() -> bool:
    is_dark_mode = config.get_is_dark_mode()
    if is_dark_mode is None:
        # No CLI configuration
        is_dark_mode = False  # pragma: no cover
    return is_dark_mode


def _make_app_ui(cli_info: CLIInfo) -> Tag:
    return ui.page_bootstrap(
        ui.head_content(
            ui.tags.link(rel="icon", href="favicon.ico"),
            ui.include_css(_shiny_root / "assets/styles.css"),
            ui.include_css(
                _shiny_root / "vendor/highlight.js/11.11.1/styles/default.min.css"
            ),
            ui.include_js(_shiny_root / "vendor/highlight.js/11.11.1/highlight.min.js"),
        ),
        ui.navset_tab(
            about_panel.about_ui(),
            dataset_panel.dataset_ui(),
            analysis_panel.analysis_ui(),
            results_panel.results_ui(),
            ui.nav_spacer(),
            ui.nav_control(
                ui.input_switch(
                    "tutorial_mode",
                    ui.tooltip(
                        tutorial_icon,
                        """
                        Tutorial mode walks you through the analysis process
                        and provides extra help along the way.
                        """,
                        placement="right",
                    ),
                    value=_get_is_tutorial_mode(cli_info),
                    width="4em",
                )
            ),
            ui.nav_control(
                ui.input_dark_mode(
                    id="dark_mode", mode="dark" if _get_is_dark_mode() else "light"
                )
            ),
            selected=dataset_panel.dataset_panel_id,
            id="top_level_nav",
        ),
        title="DP Wizard",
    )


def ctrl_c_reminder() -> None:  # pragma: no cover
    print("Session ended (Press CTRL+C to quit)")


def _make_server(cli_info: CLIInfo):
    def server(input: Inputs, output: Outputs, session: Session):  # pragma: no cover
        if cli_info.is_sample_csv:
            initial_contributions = 10
            initial_private_csv_path = package_root / ".local-config/sample.csv"
            make_sample_csv(initial_private_csv_path, initial_contributions)
            csv_info = CsvInfo(Path(initial_private_csv_path))
        else:
            initial_contributions = 1
            initial_private_csv_path = ""
            csv_info = CsvInfo(None)

        initial_product = Product.STATISTICS

        state = AppState(
            # CLI options:
            is_sample_csv=cli_info.is_sample_csv,
            in_cloud=cli_info.is_cloud_mode,
            qa_mode=cli_info.is_qa_mode,
            # Reactive bools:
            is_tutorial_mode=reactive.value(cli_info.get_is_tutorial_mode()),
            is_dataset_selected=reactive.value(False),
            is_analysis_defined=reactive.value(False),
            is_released=reactive.value(False),
            # Dataset choices:
            initial_private_csv_path=str(initial_private_csv_path),
            private_csv_path=reactive.value(str(initial_private_csv_path)),
            initial_public_csv_path="",
            public_csv_path=reactive.value(""),
            contributions=reactive.value(initial_contributions),
            contributions_entity=reactive.value("individual"),
            max_rows=reactive.value("0"),
            initial_product=initial_product,
            product=reactive.value(initial_product),
            # Analysis choices:
            csv_info=reactive.value(csv_info),
            group_column_names=reactive.value([]),
            epsilon=reactive.value(1.0),
            # Per-column choices:
            statistic_names=reactive.value({}),
            lower_bounds=reactive.value({}),
            upper_bounds=reactive.value({}),
            bin_counts=reactive.value({}),
            weights=reactive.value({}),
            analysis_errors=reactive.value({}),
            # Per-group choices:
            group_keys=reactive.value({}),
        )

        @reactive.effect
        @reactive.event(input.tutorial_mode)
        def _update_tutorial_mode():  # pyright: ignore[reportUnusedFunction]
            is_tutorial_mode = input.tutorial_mode()
            state.is_tutorial_mode.set(is_tutorial_mode)
            config.set_is_tutorial_mode(is_tutorial_mode)

        @reactive.effect
        @reactive.event(input.dark_mode)
        def _update_dark_mode():  # pyright: ignore[reportUnusedFunction]
            dark_mode = input.dark_mode()
            # Do not set state: Nothing downstream needs this.
            config.set_is_dark_mode(dark_mode == "dark")

        about_panel.about_server(input, output, session)
        dataset_panel.dataset_server(input, output, session, state)
        analysis_panel.analysis_server(input, output, session, state)
        results_panel.results_server(input, output, session, state)
        session.on_ended(ctrl_c_reminder)

    return server
