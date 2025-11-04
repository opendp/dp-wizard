from pathlib import Path

from dp_wizard_templates.code_template import Template
from shiny import reactive, ui

from dp_wizard import opendp_version, package_root
from dp_wizard.shiny.components.outputs import (
    code_sample,
    hide_if,
    info_md_box,
    tutorial_box,
)
from dp_wizard.utils.argparse_helpers import (
    PRIVATE_TEXT,
    PUBLIC_PRIVATE_TEXT,
    PUBLIC_TEXT,
)


def csv_or_columns_ui(
    in_cloud: bool,
    is_tutorial_mode: reactive.Value[bool],
):  # pragma: no cover
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
            ui.input_text_area("all_column_names", "CSV Column Names", rows=5),
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


def input_files_ui(
    is_tutorial_mode: reactive.Value[bool],
    is_sample_csv: bool,
    initial_private_csv_path: str,
    initial_public_csv_path: str,
):  # pragma: no cover
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


def csv_column_match_ui(
    csv_column_mismatch_calc,
):  # pragma: no cover
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
