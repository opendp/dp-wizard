import re
from pathlib import Path
from typing import Optional

from shiny import Inputs, Outputs, Session, reactive, render, ui

from dp_wizard.shiny.components.icons import (
    data_source_icon,
    product_icon,
    unit_of_protection_icon,
)
from dp_wizard.shiny.components.outputs import (
    code_sample,
    col_widths,
    hide_if,
    nav_button,
    only_for_screenreader,
    tutorial_box,
    warning_md_box,
)
from dp_wizard.shiny.panels.dataset_panel import data_source
from dp_wizard.types import AppState, Product
from dp_wizard.utils.argparse_helpers import (
    PRIVATE_TEXT,
    PUBLIC_PRIVATE_TEXT,
    PUBLIC_TEXT,
)
from dp_wizard.utils.code_generators import make_privacy_unit_block
from dp_wizard.utils.constraints import MAX_CONTRIBUTIONS, MAX_ROW_COUNT, MIN_ROW_COUNT
from dp_wizard.utils.csv_helper import CsvInfo, get_csv_names_mismatch
from dp_wizard.utils.shared.convert import convert_to_csv

dataset_panel_id = "dataset_panel"
OTHER = "Other"
accept = [".csv", ".tsv", ".tab"]


def int_or_zero(number_str: str) -> int:
    """
    >>> int_or_zero("1")
    1
    >>> int_or_zero("One")
    0

    This is not a general-purpose function:
    If use changes, handle more cases.

    >>> int_or_zero("1.0")
    0
    """
    try:
        number = int(number_str)
    except (TypeError, ValueError, OverflowError):
        return 0
    return number


def get_str_int_error(
    number_str: str,
    minimum: int,
    maximum: int,
    min_message: str,
    max_message: str,
) -> str | None:
    """
    >>> get_str_int_error("", 1, 10, "low", "high")
    'is required'
    >>> get_str_int_error("ABC", 1, 10, "low", "high")
    'should be an integer'
    >>> get_str_int_error("0", 1, 10, "low", "high")
    'should not be less than 1: low'
    >>> get_str_int_error("11", 1, 10, "low", "high")
    'should not be greater than 10: high'
    """
    if number_str == "":
        return "is required"
    try:
        number = int(number_str)
    except (TypeError, ValueError, OverflowError):
        return "should be an integer"
    if number < minimum:
        min_message = re.sub(r"\s+", " ", min_message).strip()
        return f"should not be less than {minimum:,}: {min_message}"
    if number > maximum:
        max_message = re.sub(r"\s+", " ", max_message).strip()
        return f"should not be greater than {maximum:,}: {max_message}"
    return None


def get_max_rows_error(number_str) -> str | None:
    """
    >>> get_max_rows_error(100)
    >>> get_max_rows_error(99)
    'Maximum row count should not be less than 100: For very small data sets, ...'
    """
    message = get_str_int_error(
        number_str=number_str,
        minimum=MIN_ROW_COUNT,
        maximum=MAX_ROW_COUNT,
        min_message="For very small data sets, too much noise would be required",
        max_message="Larger values may cause overflow during calcuations",
    )
    if message:
        return f"Maximum row count {message}."


def get_contibutions_error(number_str) -> str | None:
    """
    >>> get_contibutions_error("100")
    >>> get_contibutions_error("101")
    "... should not be greater than 100: Because the noise will be scaled ..."
    """
    message = get_str_int_error(
        number_str=number_str,
        minimum=1,
        maximum=MAX_CONTRIBUTIONS,
        min_message="This value is an upper bound on contributions",
        max_message="""
            Because the noise will be scaled by this number,
            it is much better to aggregate during preprocessing
            or to use OpenDP's truncation in your code
            than to use a large value here.
        """,
    )
    if message:
        return f"Rows per contributor {message}."


def dataset_ui():
    return ui.nav_panel(
        "Select Dataset",
        ui.output_ui("dataset_release_warning_ui"),
        ui.output_ui("welcome_ui"),
        ui.layout_columns(
            ui.card(
                ui.card_header(data_source_icon, "Data Source"),
                ui.output_ui("csv_upload_ui"),
                ui.output_ui("max_rows_tutorial_ui"),
                ui.output_ui("max_rows_input_ui"),
            ),
            [
                ui.card(
                    ui.card_header(unit_of_protection_icon, "Unit of Protection"),
                    ui.output_ui("input_entity_ui"),
                    ui.output_ui("input_contributions_ui"),
                    ui.output_ui("contributions_validation_ui"),
                    ui.output_ui("unit_of_protection_python_ui"),
                ),
                ui.card(
                    ui.card_header(product_icon, "Product"),
                    ui.output_ui("product_ui"),
                ),
            ],
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
    is_demo_csv = state.is_demo_csv

    # Reactive bools:
    is_tutorial_mode = state.is_tutorial_mode
    is_dataset_selected = state.is_dataset_selected
    # is_analysis_defined = state.is_analysis_defined
    is_released = state.is_released

    # Dataset choices:
    initial_private_path = state.initial_private_path
    private_path = state.private_path
    initial_public_path = state.initial_public_path
    public_path = state.public_path
    contributions = state.contributions
    contributions_entity = state.contributions_entity
    max_rows = state.max_rows
    initial_product = state.initial_product
    product = state.product

    # Analysis choices:
    csv_info = state.csv_info
    # group_column_names = state.group_column_names
    # epsilon = state.epsilon

    # Per-column choices:
    # (Note that these are all dicts, with the ColumnName as the key.)
    # statistic_names = state.statistic_names
    # lower_bounds = state.lower_bounds
    # upper_bounds = state.upper_bounds
    # bin_counts = state.bin_counts
    # weights = state.weights
    # analysis_errors = state.analysis_errors

    # Per-group choices:
    # (Again a dict, with ColumnName as the key.)
    # group_keys = state.group_keys

    @reactive.effect
    @reactive.event(input.public_path)
    def _on_public_path_change():
        path = Path(input.public_path()[0]["datapath"])
        if path.suffix != ".csv":
            # Histogram preview will try to read this file.
            # Convert at the start, rather than in the downstream.
            # For private files, the conversion is done in the notebook.
            path = convert_to_csv(path)
        public_path.set(str(path))
        csv_info.set(CsvInfo(path))

    @reactive.effect
    @reactive.event(input.private_path)
    def _on_private_path_change():
        path = Path(input.private_path()[0]["datapath"])
        private_path.set(str(path))
        csv_info.set(CsvInfo(path))

    @reactive.calc
    def csv_column_mismatch_calc() -> Optional[tuple[set, set]]:
        public = public_path()
        private = private_path()
        if public and private:
            just_public, just_private = get_csv_names_mismatch(
                Path(public), Path(private)
            )
            if just_public or just_private:
                return just_public, just_private

    @render.ui
    def dataset_release_warning_ui():
        return hide_if(
            not is_released(),
            warning_md_box(
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

                (If you don't need this tutorial, turn it off
                by toggling the switch in the upper right corner.)
                """,
            ),
        )

    @render.ui
    def csv_upload_ui():
        return [
            (
                warning_md_box(
                    """
                    So that private data is not accidentally uploaded,
                    the demo provides a private CSV, and does not support
                    data upload.

                    Run DP Wizard locally to process your own data.
                    """
                )
                if is_demo_csv
                else [
                    ui.markdown(
                        f"""
Choose **Private Data** {PRIVATE_TEXT}

Choose **Public Data** {PUBLIC_TEXT}

Choose both **Private Data** and **Public Data** {PUBLIC_PRIVATE_TEXT}
                        """
                    ),
                    ui.output_ui("input_files_tutorial_ui"),
                    ui.output_ui("input_files_upload_ui"),
                ]
            ),
            ui.output_ui("csv_message_ui"),
            data_source.context_code_sample(),
            ui.output_ui("python_tutorial_ui"),
        ]

    @render.ui
    def input_files_tutorial_ui():
        return tutorial_box(
            is_tutorial_mode(),
            f"""
            Internally, OpenDP works best with CSVs;
            Other formats will be converted to CSV.
            Any of these extensions are accepted:
            {', '.join(f"`{ext}`" for ext in accept)}.

            If you don't have a CSV on hand to work with,
            quit and restart with `dp-wizard --demo`,
            and DP Wizard will provide a demo CSV
            for the tutorial.
            """,
            responsive=False,
        )

    @render.ui
    def input_files_upload_ui():
        return ui.row(
            ui.input_file(
                "private_path",
                "Choose Private Data",
                accept=accept,
                placeholder=Path(initial_private_path).name,
            ),
            ui.input_file(
                "public_path",
                "Choose Public Data",
                accept=accept,
                placeholder=Path(initial_public_path).name,
            ),
        )

    @render.ui
    def csv_message_ui():
        return data_source.csv_message_ui(
            csv_column_mismatch_calc=csv_column_mismatch_calc,
            csv_messages=csv_info().get_messages(),
        )

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
        f"❓️ {OTHER}": """
            These options cover many cases, but they are just suggestions.
            Your choice here makes it easier to understand what information
            is being protected, but doesn't really affect the analysis.
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
                    only_for_screenreader("Protect privacy of this entity"),
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
        entity = contributions_entity_calc()
        entity_phrase = (
            "each instance of this entity"
            if entity == OTHER.lower()
            else f"each {entity}"
        )

        return [
            ui.markdown(
                f"""
                How many **rows** of your data can {entity_phrase} contribute to?
                """
            ),
            tutorial_box(
                is_tutorial_mode(),
                """
                For privacy to be protected, this number needs to an upper bound,
                even if not all contributors will have this many rows.
                """,
                is_demo_csv,
                """
                The `demo.csv` simulates 10 assignments
                over the course of the term for each student,
                so enter `10` here.
                """,
                responsive=False,
            ),
            ui.layout_columns(
                ui.input_text(
                    "contributions",
                    only_for_screenreader("Maximum number of rows contributed"),
                    "",
                ),
                [],  # Column placeholder
                col_widths=col_widths,  # type: ignore
            ),
        ]

    @reactive.effect
    @reactive.event(input.contributions)
    def _on_contributions_change():
        contributions.set(int_or_zero(input.contributions()))

    @reactive.effect
    @reactive.event(input.entity)
    def _on_contributions_entity_change():
        contributions_entity.set(contributions_entity_calc())

    @reactive.calc
    def contributions_entity_calc() -> str:
        # The "[2:]" removes the leading emoji and space.
        return input.entity()[2:].lower().strip()

    @reactive.effect
    def set_is_dataset_selected():
        info = csv_info()
        is_dataset_selected.set(
            not get_contibutions_error(input.contributions())
            and not info.get_is_error()
            and len(info.get_all_column_names()) > 0
            and not get_max_rows_error(input.max_rows())
            and not csv_column_mismatch_calc()
        )

    @render.ui
    def contributions_validation_ui():
        error = get_contibutions_error(input.contributions())
        if error:
            return warning_md_box(error)

    @render.ui
    def python_tutorial_ui():
        return tutorial_box(
            is_tutorial_mode(),
            """
            Along the way, code samples demonstrate
            how the information you provide is used in the
            OpenDP Library, and at the end you can download
            a notebook for the entire calculation.
            """,
            responsive=False,
        )

    @reactive.effect
    @reactive.event(input.max_rows)
    def _on_max_rows_change():
        max_rows.set(int_or_zero(input.max_rows()))

    @render.ui
    def max_rows_validation_ui():
        error_md = get_max_rows_error(input.max_rows())
        if error_md:
            return warning_md_box(error_md)

    @render.ui
    def max_rows_tutorial_ui():
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
        )

    @render.ui
    def max_rows_input_ui():
        return (
            ui.layout_columns(
                ui.input_text(
                    "max_rows",
                    only_for_screenreader("Maximum number of rows in CSV"),
                    "",
                ),
                [],  # column placeholder
                col_widths=col_widths,  # type: ignore
            ),
            ui.output_ui("max_rows_validation_ui"),
        )

    @render.ui
    def define_analysis_button_ui():
        enabled = is_dataset_selected()
        button = nav_button("go_to_analysis", "Define Analysis", disabled=not enabled)
        if enabled:
            return button
        return [
            button,
            """
            Specify CSV, unit of protection,
            and maximum row count before proceeding.
            """,
        ]

    @render.ui
    def unit_of_protection_python_ui():
        return code_sample(
            "Unit of Protection",
            make_privacy_unit_block(
                contributions=contributions(),
                contributions_entity=contributions_entity_calc(),
            ),
        )

    @render.ui
    def product_ui():
        return [
            ui.markdown(
                """
                What type of analysis do you want?
                """
            ),
            ui.input_radio_buttons(
                "product",
                only_for_screenreader("Type of analysis"),
                Product.to_dict(),
                selected=str(initial_product.value),
            ),
            tutorial_box(
                is_tutorial_mode(),
                """
                Although the underlying OpenDP library is very flexible,
                DP Wizard offers only a few analysis options:

                - The **DP Statistics** option supports
                  grouping, histograms, mean, and median.
                - With **DP Synthetic Data**, your privacy budget is used
                  to infer the distributions of values within the
                  selected columns, and the correlations between columns.
                  This is less accurate than calculating the desired
                  statistics directly, but can be easier to work with downstream.
                """,
                responsive=False,
            ),
        ]

    @reactive.effect
    @reactive.event(input.product)
    def _on_product_change():
        product.set(Product(int(input.product())))

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
