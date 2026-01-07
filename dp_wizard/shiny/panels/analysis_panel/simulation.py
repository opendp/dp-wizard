from pathlib import Path

from shiny import reactive, ui

from dp_wizard.shiny.components.icons import simulation_icon
from dp_wizard.shiny.components.outputs import tutorial_box
from dp_wizard.utils.csv_helper import get_csv_row_count


def simulation_card_ui(
    is_tutorial_mode: reactive.Value[bool],
    public_csv_path: reactive.Value[str],
):
    help = (
        tutorial_box(
            is_tutorial_mode(),
            """
            Unlike the other settings on this page,
            this estimate **is not used** in the final calculation.

            Until you make a release, your CSV will not be
            read except to determine the names of columns,
            but the number of rows does have implications for the
            accuracy which DP can provide with a given privacy budget.
            """,
            responsive=False,
        ),
    )
    if public_csv_path():
        row_count_str = str(get_csv_row_count(Path(public_csv_path())))
        inner = [
            ui.markdown(
                f"""
                Because you've provided a public CSV,
                it *will be read* to generate previews.

                The confidence interval depends on the number of rows.
                Your public CSV has {row_count_str} rows,
                but if you believe the private CSV will be
                much larger or smaller, please update.
                """
            ),
            ui.input_select(
                "row_count",
                "Estimated Rows",
                choices=[row_count_str, "100", "1000", "10000"],
                selected=row_count_str,
            ),
            help,
        ]
    else:
        inner = [
            ui.markdown(
                """
                What is the approximate number of rows in the dataset?
                This number is only used for the simulation
                and not the final calculation.
                """
            ),
            ui.input_select(
                "row_count",
                "Estimated Rows",
                choices=["100", "1000", "10000"],
                selected="100",
            ),
            help,
        ]
    return ui.card(
        ui.card_header(simulation_icon, "Simulation"),
        inner,
    )
