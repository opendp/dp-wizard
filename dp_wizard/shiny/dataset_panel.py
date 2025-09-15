from pathlib import Path
from typing import Optional

from dp_wizard_templates.code_template import Template
from shiny import Inputs, Outputs, Session, reactive, render, ui

from dp_wizard import opendp_version
from dp_wizard.shiny.components.outputs import (
    code_sample,
    col_widths,
    hide_if,
    info_md_box,
    nav_button,
    tutorial_box,
)
from dp_wizard.types import AppState
from dp_wizard.utils.argparse_helpers import (
    PRIVATE_TEXT,
    PUBLIC_PRIVATE_TEXT,
    PUBLIC_TEXT,
)
from dp_wizard.utils.code_generators import make_privacy_unit_block
from dp_wizard.utils.csv_helper import get_csv_names_mismatch, read_csv_names

dataset_panel_id = "dataset_panel"


def get_pos_int_error(number_str, minimum=100):
    """
    If the inputs are numeric, I think shiny converts
    any strings that can't be parsed to numbers into None,
    so the "should be a number" errors may not be seen in practice.
    >>> get_pos_int_error('100')
    >>> get_pos_int_error('0')
    'should be at least 100'
    >>> get_pos_int_error(None)
    'is required'
    >>> get_pos_int_error('')
    'is required'
    >>> get_pos_int_error('100.1')
    'should be an integer'
    """
    if number_str is None or number_str == "":
        return "is required"
    try:
        number = int(number_str)
    except (TypeError, ValueError, OverflowError):
        return "should be an integer"
    if number < minimum:
        return f"should be at least {minimum}"
    return None


def get_row_count_errors(max_rows):
    """
    >>> get_row_count_errors(100)
    []
    >>> get_row_count_errors('xyz')
    ['Maximum row count should be an integer.']
    >>> get_row_count_errors(None)
    ['Maximum row count is required.']
    """
    messages = []
    if error := get_pos_int_error(max_rows):
        messages.append(f"Maximum row count {error}.")
    return messages


def dataset_ui():
    return ui.nav_panel(
        "Select Dataset",
        ui.output_ui("dataset_release_warning_ui"),
        ui.output_ui("welcome_ui"),
        ui.layout_columns(
            ui.card(
                ui.card_header("Data Source"),
                ui.output_ui("csv_or_columns_ui"),
                ui.output_ui("row_count_bounds_ui"),
            ),
            ui.card(
                ui.card_header("Unit of Privacy"),
                ui.output_ui("input_entity_ui"),
                ui.output_ui("input_contributions_ui"),
                ui.output_ui("contributions_validation_ui"),
                ui.output_ui("unit_of_privacy_python_ui"),
            ),
        ),
        ui.output_ui("define_analysis_button_ui"),
        value="dataset_panel",
    )


def dataset_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    state: AppState,
):  # pragma: no cover
    # CLI options:
    is_sample_csv = state.is_sample_csv
    in_cloud = state.in_cloud

    # Top-level:
    is_tutorial_mode = state.is_tutorial_mode

    # Dataset choices:
    initial_private_csv_path = state.initial_private_csv_path
    private_csv_path = state.private_csv_path
    initial_public_csv_path = state.initial_public_csv_path
    public_csv_path = state.public_csv_path
    contributions = state.contributions
    max_rows = state.max_rows

    # Analysis choices:
    column_names = state.column_names
    # groups = state.groups
    # epsilon = state.epsilon

    # Per-column choices:
    # (Note that these are all dicts, with the ColumnName as the key.)
    # analysis_types = state.analysis_types
    # lower_bounds = state.lower_bounds
    # upper_bounds = state.upper_bounds
    # bin_counts = state.bin_counts
    # weights = state.weights
    # analysis_errors = state.analysis_errors

    # Release state:
    # synthetic_data = state.synthetic_data
    released = state.released

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

    @render.ui
    def dataset_release_warning_ui():
        return hide_if(
            not released(),
            info_md_box(
                """
                After making a differentially private release,
                changes to the dataset will constitute a new release,
                and an additional epsilon spend.
                """
            ),
        )

    @render.ui
    def welcome_ui():
        return (
            tutorial_box(
                is_tutorial_mode(),
                """
                Welcome to **DP Wizard**, from OpenDP.

                DP Wizard makes it easier to get started with
                differential privacy: You configure a basic analysis
                interactively, and then download code which
                demonstrates how to use the
                [OpenDP Library](https://docs.opendp.org/).

                (If you don't need these extra help messages,
                turn them off by toggling the switch in the upper right
                corner of the window.)
                """,
            ),
        )

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
                    Path(__file__).parent.parent / "utils/code_generators/no-tests",
                )
                .fill_values(CSV_PATH="sample.csv")
                .fill_expressions(
                    MARGINS_LIST="margins",
                    EXTRA_COLUMNS="extra_columns",
                    OPENDP_VERSION=opendp_version,
                    WEIGHTS="weights",
                )
                .fill_blocks(
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

    entities = {
        "📅 Individual Per Period": """
            You can use differential privacy to protect your data
            over specific time periods.
            This may improve accuracy and be easier to implement
            when individuals don’t have unique IDs.
            """,
        "👤 Individual": """
            Differential privacy is often used to protect your privacy
            as an individual, but depending on your needs,
            you might want to protect a smaller or larger entity.
            """,
        "🏠 Household": """
            If someone in your household has their privacy violated,
            you might feel that your own privacy is also compromised.
            In that case, you may prefer to protect your entire household
            rather than just yourself.
            """,
    }

    @render.ui
    def input_entity_ui():
        return [
            ui.markdown(
                """
                Next, what is the **entity** whose privacy you want to protect?
                """
            ),
            ui.layout_columns(
                ui.input_select(
                    "entity",
                    None,
                    list(entities.keys()),
                    selected="👤 Individual",
                ),
                ui.output_ui("entity_info_ui"),
                col_widths=col_widths,  # type: ignore
            ),
        ]

    @render.ui
    def entity_info_ui():
        return ui.markdown(entities[input.entity()])

    @render.ui
    def input_contributions_ui():
        entity = input.entity()[2:].lower()

        return [
            ui.markdown(
                f"""
                How many **rows** of the CSV can each {entity} contribute to?
                This is the "unit of privacy" which will be protected.
                """
            ),
            tutorial_box(
                is_tutorial_mode(),
                """
                A larger number here will add more noise
                to the released statistics, to ensure that
                the contribution of any single individual is masked.
                """,
                is_sample_csv,
                """
                The `sample.csv` simulates 10 assignments
                over the course of the term for each student,
                so enter `10` here.
                """,
                responsive=False,
            ),
            ui.layout_columns(
                ui.input_numeric(
                    "contributions",
                    None,
                    contributions(),
                    min=1,
                ),
                [],  # Column placeholder
                col_widths=col_widths,  # type: ignore
            ),
        ]

    @reactive.effect
    @reactive.event(input.contributions)
    def _on_contributions_change():
        contributions.set(input.contributions())

    @reactive.calc
    def button_enabled():
        return (
            contributions_valid()
            and not get_row_count_errors(max_rows())
            and len(column_names()) > 0
            and (in_cloud or not csv_column_mismatch_calc())
        )

    @reactive.calc
    def contributions_valid():
        contributions = input.contributions()
        return isinstance(contributions, int) and contributions >= 1

    @render.ui
    def contributions_validation_ui():
        return hide_if(
            contributions_valid(),
            info_md_box("Contributions must be 1 or greater."),
        )

    @render.ui
    def python_tutorial_ui():
        cloud_extra_markdown = (
            """
            Because this instance of DP Wizard is running in the cloud,
            we don't allow private data to be uploaded.
            When run locally, DP Wizard can also run an analysis
            on your data and return results,
            and not just an unexecuted notebook.
            """
            if in_cloud
            else ""
        )
        return tutorial_box(
            is_tutorial_mode(),
            f"""
            Along the way, code samples demonstrate
            how the information you provide is used in the
            OpenDP Library, and at the end you can download
            a notebook for the entire calculation.

            {cloud_extra_markdown}
            """,
            responsive=False,
        )

    @reactive.effect
    @reactive.event(input.max_rows)
    def _on_max_rows_change():
        max_rows.set(input.max_rows())

    @render.ui
    def optional_row_count_error_ui():
        error_md = "\n".join(f"- {error}" for error in get_row_count_errors(max_rows()))
        if error_md:
            return info_md_box(error_md)

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
                    large, the delta parameter should be increased
                    correspondingly.
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
                    None,
                    "0",
                ),
                [],  # column placeholder
                col_widths=col_widths,  # type: ignore
            ),
            ui.output_ui("optional_row_count_error_ui"),
        )

    @render.ui
    def define_analysis_button_ui():
        enabled = button_enabled()
        button = nav_button("go_to_analysis", "Define analysis", disabled=not enabled)
        if enabled:
            return button
        return [
            button,
            f"""
            Specify {'columns' if in_cloud else 'CSV'}, unit of privacy,
            and maximum row count before proceeding.
            """,
        ]

    @render.ui
    def unit_of_privacy_python_ui():
        return code_sample("Unit of Privacy", make_privacy_unit_block(contributions()))

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
