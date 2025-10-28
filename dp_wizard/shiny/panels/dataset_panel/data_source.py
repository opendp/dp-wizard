from pathlib import Path
from typing import Optional

from dp_wizard_templates.code_template import Template
from shiny import Inputs, Outputs, Session, reactive, render, ui

from dp_wizard import opendp_version, package_root
from dp_wizard.shiny.components.icons import data_source_icon
from dp_wizard.shiny.components.outputs import (
    code_sample,
    col_widths,
    hide_if,
    info_md_box,
    only_for_screenreader,
    tutorial_box,
)
from dp_wizard.types import AppState
from dp_wizard.utils.argparse_helpers import (
    PRIVATE_TEXT,
    PUBLIC_PRIVATE_TEXT,
    PUBLIC_TEXT,
)
from dp_wizard.utils.csv_helper import get_csv_names_mismatch, read_csv_names


def data_source_ui():
    return ui.card(
        ui.card_header(data_source_icon, "Data Source"),
        ui.output_ui("csv_or_columns_ui"),
        ui.output_ui("row_count_bounds_ui"),
    )


def data_source_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    state: AppState,
):  # pragma: no cover
    is_sample_csv = state.is_sample_csv
    in_cloud = state.in_cloud
    is_tutorial_mode = state.is_tutorial_mode
    initial_private_csv_path = state.initial_private_csv_path
    private_csv_path = state.private_csv_path
    initial_public_csv_path = state.initial_public_csv_path
    public_csv_path = state.public_csv_path
    column_names = state.column_names
    max_rows = state.max_rows

    @render.ui
    def csv_or_columns_ui():
        if in_cloud:
            content = [
                ui.markdown(
                    """
                    Provide the names of columns you'll use in your analysis,
                    one per line, with no extra punctuation.
                    """
                ),
                tutorial_box(
                    is_tutorial_mode(),
                    """
                    When [installed and run
                    locally](https://pypi.org/project/dp_wizard/),
                    DP Wizard allows you to specify a private and public CSV,
                    but for the safety of your data, in the cloud
                    DP Wizard only accepts column names.

                    If you don't have other ideas, we can imagine
                    a CSV of student quiz grades: Enter `student_id`,
                    `quiz_id`, `grade`, and `class_year_str` below,
                    each on a separate line.
                    """,
                    responsive=False,
                ),
                ui.input_text_area("column_names", "CSV Column Names", rows=5),
            ]
        else:
            content = [
                ui.markdown(
                    f"""
Choose **Private CSV** {PRIVATE_TEXT}

Choose **Public CSV** {PUBLIC_TEXT}

Choose both **Private CSV** and **Public CSV** {PUBLIC_PRIVATE_TEXT}
                    """
                ),
                ui.output_ui("input_files_ui"),
                ui.output_ui("csv_column_match_ui"),
            ]

        content += [
            code_sample(
                "Context",
                Template(
                    # NOTE: If stats vs. synth is moved to the top of the flow,
                    # then we can show the appropriate template here.
                    "stats_context",
                    package_root / "utils/code_generators/no-tests",
                )
                .fill_values(CSV_PATH="sample.csv")
                .fill_expressions(
                    MARGINS_LIST="margins",
                    EXTRA_COLUMNS="extra_columns",
                    OPENDP_V_VERSION=f"v{opendp_version}",
                    WEIGHTS="weights",
                )
                .fill_code_blocks(
                    PRIVACY_UNIT_BLOCK="",
                    PRIVACY_LOSS_BLOCK="",
                    OPTIONAL_CSV_BLOCK=(
                        "# More of these slots will be filled in\n"
                        "# as you move through DP Wizard.\n"
                    ),
                )
                .finish()
                .strip(),
            ),
            ui.output_ui("python_tutorial_ui"),
        ]
        return content

    @render.ui
    def input_files_ui():
        # We can't set the actual value of a file input,
        # but the placeholder string is a good substitute.
        #
        # Make sure this doesn't depend on reactive values,
        # for two reasons:
        # - If there is a dependency, the inputs are redrawn,
        #   and it looks like the file input is unset.
        # - After file upload, the internal copy of the file
        #   is renamed to something like "0.csv".
        return [
            tutorial_box(
                is_tutorial_mode(),
                (
                    """
                    For the tutorial, we've provided the grades
                    on assignments for a school class in `sample.csv`.
                    You don't need to upload an additional file.
                    """
                    if is_sample_csv
                    else """
                    If you don't have a CSV on hand to work with,
                    quit and restart with `dp-wizard --sample`,
                    and DP Wizard will provide a sample CSV
                    for the tutorial.
                    """
                ),
                responsive=False,
            ),
            ui.row(
                ui.input_file(
                    "private_csv_path",
                    "Choose Private CSV",
                    accept=[".csv"],
                    placeholder=Path(initial_private_csv_path).name,
                ),
                ui.input_file(
                    "public_csv_path",
                    "Choose Public CSV",
                    accept=[".csv"],
                    placeholder=Path(initial_public_csv_path).name,
                ),
            ),
        ]

    @render.ui
    def csv_column_match_ui():
        mismatch = csv_column_mismatch_calc()
        messages = []
        if mismatch:
            just_public, just_private = mismatch
            if just_public:
                messages.append(
                    "- Only the public CSV contains: "
                    + ", ".join(f"`{name}`" for name in just_public)
                )
            if just_private:
                messages.append(
                    "- Only the private CSV contains: "
                    + ", ".join(f"`{name}`" for name in just_private)
                )
        return hide_if(not messages, info_md_box("\n".join(messages)))

    @render.ui
    def row_count_bounds_ui():
        return (
            ui.markdown("What is the **maximum row count** of your CSV?"),
            tutorial_box(
                is_tutorial_mode(),
                """
                If you're unsure, pick a safe value, like the total
                population of the group being analyzed.

                This value is used downstream two ways:
                - There is a very small probability that data could be
                    released verbatim. If your dataset is particularly
                    large, this probability should be even smaller.
                - The floating point numbers used by computers are not the
                    same as the real numbers of mathematics, and with very
                    large datasets, this gap accumulates, and more noise is
                    necessary.
                """,
                responsive=False,
            ),
            ui.layout_columns(
                ui.input_text(
                    "max_rows",
                    only_for_screenreader("Maximum number of rows in CSV"),
                    "0",
                ),
                [],  # column placeholder
                col_widths=col_widths,  # type: ignore
            ),
            ui.output_ui("optional_row_count_error_ui"),
        )

    @reactive.effect
    @reactive.event(input.public_csv_path)
    def _on_public_csv_path_change():
        path = input.public_csv_path()[0]["datapath"]
        public_csv_path.set(path)
        column_names.set(read_csv_names(Path(path)))

    @reactive.effect
    @reactive.event(input.private_csv_path)
    def _on_private_csv_path_change():
        path = input.private_csv_path()[0]["datapath"]
        private_csv_path.set(path)
        column_names.set(read_csv_names(Path(path)))

    @reactive.effect
    @reactive.event(input.column_names)
    def _on_column_names_change():
        column_names.set(
            [
                clean
                for line in input.column_names().splitlines()
                if (clean := line.strip())
            ]
        )

    @reactive.effect
    @reactive.event(input.max_rows)
    def _on_max_rows_change():
        max_rows.set(input.max_rows())

    @reactive.calc
    def csv_column_mismatch_calc() -> Optional[tuple[set, set]]:
        public = public_csv_path()
        private = private_csv_path()
        if public and private:
            just_public, just_private = get_csv_names_mismatch(
                Path(public), Path(private)
            )
            if just_public or just_private:
                return just_public, just_private
