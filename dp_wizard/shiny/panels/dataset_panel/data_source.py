from dp_wizard_templates.code_template import Template
from shiny import reactive, ui

from dp_wizard import opendp_version, package_root
from dp_wizard.shiny.components.outputs import code_sample, tutorial_box
from dp_wizard.utils.argparse_helpers import (
    PRIVATE_TEXT,
    PUBLIC_PRIVATE_TEXT,
    PUBLIC_TEXT,
)


def csv_or_columns_ui(in_cloud: bool, is_tutorial_mode: reactive.Value[bool]):
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
