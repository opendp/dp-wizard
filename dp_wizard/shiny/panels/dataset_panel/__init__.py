from shiny import Inputs, Outputs, Session, reactive, render, ui

from dp_wizard.shiny.components.icons import (
    product_icon,
    unit_of_privacy_icon,
)
from dp_wizard.shiny.components.outputs import (
    code_sample,
    col_widths,
    hide_if,
    info_md_box,
    nav_button,
    only_for_screenreader,
    tutorial_box,
)
from dp_wizard.shiny.panels.dataset_panel.data_source import (
    data_source_server,
    data_source_ui,
)
from dp_wizard.types import AppState, Product
from dp_wizard.utils.code_generators import make_privacy_unit_block

dataset_panel_id = "dataset_panel"


def get_pos_int_error(number_str, minimum=100) -> str | None:
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


def get_row_count_errors(max_rows) -> list[str]:
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
            data_source_ui(),
            [
                ui.card(
                    ui.card_header(unit_of_privacy_icon, "Unit of Privacy"),
                    ui.output_ui("input_entity_ui"),
                    ui.output_ui("input_contributions_ui"),
                    ui.output_ui("contributions_validation_ui"),
                    ui.output_ui("unit_of_privacy_python_ui"),
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
    is_sample_csv = state.is_sample_csv
    in_cloud = state.in_cloud

    # Top-level:
    is_tutorial_mode = state.is_tutorial_mode

    # Dataset choices:
    # initial_private_csv_path = state.initial_private_csv_path
    # private_csv_path = state.private_csv_path
    # initial_public_csv_path = state.initial_public_csv_path
    # public_csv_path = state.public_csv_path
    contributions = state.contributions
    contributions_entity = state.contributions_entity
    max_rows = state.max_rows
    initial_product = state.initial_product
    product = state.product

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
    released = state.released

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
                    only_for_screenreader("Maximum number of rows contributed"),
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

    @reactive.effect
    @reactive.event(input.entity)
    def _on_contributions_entity_change():
        contributions_entity.set(contributions_entity_calc())

    @reactive.calc
    def contributions_entity_calc() -> str:
        return input.entity()[2:].lower()

    @reactive.calc
    def button_enabled():
        return (
            contributions_valid()
            and not get_row_count_errors(max_rows())
            and len(column_names()) > 0
            # TODO: Do per-card validation and re-enable:
            # and (in_cloud or not csv_column_mismatch_calc())
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

    @render.ui
    def optional_row_count_error_ui():
        error_md = "\n".join(f"- {error}" for error in get_row_count_errors(max_rows()))
        if error_md:
            return info_md_box(error_md)

    @render.ui
    def define_analysis_button_ui():
        enabled = button_enabled()
        button = nav_button("go_to_analysis", "Define Analysis", disabled=not enabled)
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
        return code_sample(
            "Unit of Privacy",
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
                  grouping, histograms, mean, median, and count.
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

    data_source_server(input, output, session, state)
