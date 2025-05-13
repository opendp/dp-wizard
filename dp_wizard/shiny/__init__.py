from pathlib import Path
import csv
import random

from shiny import ui, reactive, Inputs, Outputs, Session

from dp_wizard.utils.argparse_helpers import CLIInfo
from dp_wizard.utils.csv_helper import read_csv_names
from dp_wizard.shiny import (
    about_panel,
    analysis_panel,
    dataset_panel,
    results_panel,
)


app_ui = ui.page_bootstrap(
    ui.head_content(ui.include_css(Path(__file__).parent / "css" / "styles.css")),
    ui.navset_tab(
        about_panel.about_ui(),
        dataset_panel.dataset_ui(),
        analysis_panel.analysis_ui(),
        results_panel.results_ui(),
        selected=dataset_panel.dataset_panel_id,
        id="top_level_nav",
    ),
    title="DP Wizard",
)


def ctrl_c_reminder():  # pragma: no cover
    print("Session ended (Press CTRL+C to quit)")


def _make_demo_csv(path: Path, contributions):
    """
    >>> import tempfile
    >>> from pathlib import Path
    >>> import csv
    >>> with tempfile.NamedTemporaryFile() as temp:
    ...     _make_demo_csv(Path(temp.name), 10)
    ...     with open(temp.name, newline="") as csv_handle:
    ...         reader = csv.DictReader(csv_handle)
    ...         reader.fieldnames
    ...         rows = list(reader)
    ...         rows[0].values()
    ...         rows[-1].values()
    ['student_id', 'class_year', 'hw_number', 'grade', 'self_assessment']
    dict_values(['1', '2', '1', '82', '0'])
    dict_values(['100', '2', '10', '78', '0'])
    """
    random.seed(0)  # So the mock data will be stable across runs.
    with path.open("w", newline="") as demo_handle:
        fields = ["student_id", "class_year", "hw_number", "grade", "self_assessment"]
        writer = csv.DictWriter(demo_handle, fieldnames=fields)
        writer.writeheader()
        for student_id in range(1, 101):
            class_year = int(_clip(random.gauss(2, 1), 1, 4))
            for hw_number in range(1, contributions + 1):
                # Older students do slightly better in the class,
                # but each assignment gets harder.
                mean_grade = random.gauss(90, 5) + class_year * 2 - hw_number
                grade = int(_clip(random.gauss(mean_grade, 5), 0, 100))
                self_assessment = 1 if grade > 90 and random.random() > 0.1 else 0
                writer.writerow(
                    {
                        "student_id": student_id,
                        "class_year": class_year,
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


def make_server_from_cli_info(cli_info: CLIInfo):
    def server(input: Inputs, output: Outputs, session: Session):  # pragma: no cover
        if cli_info.is_demo:
            initial_contributions = 10
            initial_private_csv_path = Path(__file__).parent.parent / "tmp" / "demo.csv"
            _make_demo_csv(initial_private_csv_path, initial_contributions)
            initial_column_names = read_csv_names(Path(initial_private_csv_path))
        else:
            initial_contributions = 1
            initial_private_csv_path = ""
            initial_column_names = []

        contributions = reactive.value(initial_contributions)
        private_csv_path = reactive.value(str(initial_private_csv_path))
        column_names = reactive.value(initial_column_names)

        public_csv_path = reactive.value("")
        analysis_types = reactive.value({})
        lower_bounds = reactive.value({})
        upper_bounds = reactive.value({})
        bin_counts = reactive.value({})
        groups = reactive.value([])
        weights = reactive.value({})
        epsilon = reactive.value(1.0)
        released = reactive.value(False)

        about_panel.about_server(
            input,
            output,
            session,
        )
        dataset_panel.dataset_server(
            input,
            output,
            session,
            released=released,
            is_demo=cli_info.is_demo,
            in_cloud=cli_info.in_cloud,
            initial_public_csv_path="",
            initial_private_csv_path=str(initial_private_csv_path),
            public_csv_path=public_csv_path,
            private_csv_path=private_csv_path,
            column_names=column_names,
            contributions=contributions,
        )
        analysis_panel.analysis_server(
            input,
            output,
            session,
            released=released,
            is_demo=cli_info.is_demo,
            public_csv_path=public_csv_path,
            column_names=column_names,
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
            released=released,
            in_cloud=cli_info.in_cloud,
            qa_mode=cli_info.qa_mode,
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
        session.on_ended(ctrl_c_reminder)

    return server
