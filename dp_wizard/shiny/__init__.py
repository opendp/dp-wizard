import csv
import random
import re
from collections import defaultdict
from pathlib import Path

from faicons import icon_svg
from shiny import App, Inputs, Outputs, Session, reactive, ui

from dp_wizard.shiny import (
    about_panel,
    analysis_panel,
    dataset_panel,
    results_panel,
)
from dp_wizard.types import AppState
from dp_wizard.utils.argparse_helpers import CLIInfo
from dp_wizard.utils.csv_helper import read_csv_names

_assets_path = Path(__file__).parent / "assets"
assert _assets_path.exists()


def make_app(cli_info: CLIInfo):
    return App(
        _make_app_ui(cli_info),
        _make_server(cli_info),
        static_assets=_assets_path,
    )


def _make_app_ui(cli_info: CLIInfo):
    root = Path(__file__).parent
    return ui.page_bootstrap(
        ui.head_content(
            ui.tags.link(rel="icon", href="favicon.ico"),
            ui.include_css(root / "assets/styles.css"),
            ui.include_css(root / "vendor/highlight.js/11.11.1/styles/default.min.css"),
            ui.include_js(root / "vendor/highlight.js/11.11.1/highlight.min.js"),
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
                        icon_svg("circle-question"),
                        """
                        Tutorial mode walks you through the analysis process
                        and provides extra help along the way.
                        """,
                        placement="right",
                    ),
                    value=cli_info.get_is_tutorial_mode(),
                    width="4em",
                )
            ),
            ui.nav_control(ui.input_dark_mode()),
            selected=dataset_panel.dataset_panel_id,
            id="top_level_nav",
        ),
        title="DP Wizard",
    )


def ctrl_c_reminder():  # pragma: no cover
    print("Session ended (Press CTRL+C to quit)")


def _make_sample_csv(path: Path, contributions):
    """
    >>> import tempfile
    >>> from pathlib import Path
    >>> import csv
    >>> with tempfile.NamedTemporaryFile() as temp:
    ...     _make_sample_csv(Path(temp.name), 10)
    ...     with open(temp.name, newline="") as csv_handle:
    ...         reader = csv.DictReader(csv_handle)
    ...         reader.fieldnames
    ...         rows = list(reader)
    ...         rows[0].values()
    ...         rows[-1].values()
    ['student_id', 'class_year_str', 'hw_number', 'grade', 'self_assessment']
    dict_values(['1', 'sophomore', '1', '82', '0'])
    dict_values(['100', 'sophomore', '10', '78', '0'])
    """
    random.seed(0)  # So the mock data will be stable across runs.
    with path.open("w", newline="") as sample_csv_handle:
        fields = [
            "student_id",
            "class_year_str",
            "hw_number",
            "grade",
            "self_assessment",
        ]
        class_year_map = ["first year", "sophomore", "junior", "senior"]
        writer = csv.DictWriter(sample_csv_handle, fieldnames=fields)
        writer.writeheader()
        for student_id in range(1, 101):
            class_year = int(_clip(random.gauss(1, 1), 0, 3))
            for hw_number in range(1, contributions + 1):
                # Older students do slightly better in the class,
                # but each assignment gets harder.
                mean_grade = random.gauss(90, 5) + (class_year + 1) * 2 - hw_number
                grade = int(_clip(random.gauss(mean_grade, 5), 0, 100))
                self_assessment = 1 if grade > 90 and random.random() > 0.1 else 0
                writer.writerow(
                    {
                        "student_id": student_id,
                        "class_year_str": class_year_map[class_year],
                        "hw_number": hw_number,
                        "grade": grade,
                        "self_assessment": self_assessment,
                    }
                )


def _clip(n: float, lower_bound: float, upper_bound: float) -> float:
    """
    >>> _clip(-5, 0, 10)
    0
    >>> _clip(5, 0, 10)
    5
    >>> _clip(15, 0, 10)
    10
    """
    return max(min(n, upper_bound), lower_bound)


def _scan_text_for_input_ids(text, rel_path, errors):
    """
    >>> text = '''
    ... ui.input_text("spill")
    ... @reactive.event(input.spell)
    ... '''
    >>> rel_path = 'fake/component.py'
    >>> errors = []
    >>> _scan_text_for_input_ids(text, rel_path, errors)
    >>> errors
    ['fake/component.py:2 includes "input.spell", but there is no "spell" id']
    """
    lines = text.splitlines()
    props = defaultdict(list)
    for number, line in enumerate(lines):
        if line.strip().startswith("..."):
            continue
        for match in re.findall(r"input\.(\w+)", line):
            props[match].append(str(number))
    for prop in props.keys():
        if f'"{prop}"' not in text:
            errors.append(
                f'{rel_path}:{",".join(props[prop])} includes '
                f'"input.{prop}", but there is no "{prop}" id'
            )


def _scan_files_for_input_ids():
    """
    A really hacky scan of the source code to find IDs with typos.
    There is an issue filed with Shiny, but no comments since May 2024:

    "If an nonexistent input is accessed in an output, no error is printed"
    https://github.com/posit-dev/py-shiny/issues/400

    This is only checking in one direction, but picking out strings
    that are used as IDs and then looking for "inputs" would be much more work.
    """
    errors = []
    for path in Path(__file__).parent.glob("**/*.py"):
        text = path.read_text()
        rel_path = path.relative_to(Path(__file__).parent)
        _scan_text_for_input_ids(text, rel_path, errors)
    if errors:  # pragma: no cover
        raise Exception("\n".join(errors))


def _make_server(cli_info: CLIInfo):
    _scan_files_for_input_ids()

    def server(input: Inputs, output: Outputs, session: Session):  # pragma: no cover
        if cli_info.is_sample_csv:
            initial_contributions = 10
            initial_private_csv_path = (
                Path(__file__).parent.parent / "tmp" / "sample.csv"
            )
            _make_sample_csv(initial_private_csv_path, initial_contributions)
            initial_column_names = read_csv_names(Path(initial_private_csv_path))
        else:
            initial_contributions = 1
            initial_private_csv_path = ""
            initial_column_names = []

        state = AppState(
            # CLI options:
            is_sample_csv=cli_info.is_sample_csv,
            in_cloud=cli_info.is_cloud_mode,
            qa_mode=cli_info.is_qa_mode,
            # Top-level:
            is_tutorial_mode=reactive.value(cli_info.get_is_tutorial_mode()),
            # Dataset choices:
            initial_private_csv_path=str(initial_private_csv_path),
            private_csv_path=reactive.value(str(initial_private_csv_path)),
            initial_public_csv_path="",
            public_csv_path=reactive.value(""),
            contributions=reactive.value(initial_contributions),
            max_rows=reactive.value("0"),
            # Analysis choices:
            column_names=reactive.value(initial_column_names),
            groups=reactive.value([]),
            epsilon=reactive.value(1.0),
            # Per-column choices:
            analysis_types=reactive.value({}),
            lower_bounds=reactive.value({}),
            upper_bounds=reactive.value({}),
            bin_counts=reactive.value({}),
            weights=reactive.value({}),
            analysis_errors=reactive.value({}),
            # Release state:
            synthetic_data=reactive.value(False),
            released=reactive.value(False),
        )

        @reactive.effect
        @reactive.event(input.tutorial_mode)
        def _update_tutorial_mode():
            state.is_tutorial_mode.set(input.tutorial_mode())

        about_panel.about_server(input, output, session)
        dataset_panel.dataset_server(input, output, session, state)
        analysis_panel.analysis_server(input, output, session, state)
        results_panel.results_server(input, output, session, state)
        session.on_ended(ctrl_c_reminder)

    return server
