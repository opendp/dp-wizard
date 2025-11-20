import re

from shiny import Inputs, Outputs, Session, module, reactive, render, ui

from dp_wizard.shiny.components.icons import (
    column_config_icon,
)
from dp_wizard.shiny.components.outputs import only_for_screenreader

# from dp_wizard.shiny.components.outputs import (
#     code_sample,
#     col_widths,
#     hide_if,
#     info_md_box,
#     only_for_screenreader,
#     tutorial_box,
# )
from dp_wizard.types import ColumnName

# from shiny.types import SilentException


# from dp_wizard.utils.code_generators import make_column_config_block
# from dp_wizard.utils.code_generators.analyses import (
#     get_analysis_by_name,
#     histogram,
#     mean,
#     median,
# )
# from dp_wizard.utils.dp_helper import confidence, make_accuracy_histogram
# from dp_wizard.utils.mock_data import ColumnDef, mock_data
# from dp_wizard.utils.shared import plot_bars


@module.ui
def group_ui():  # pragma: no cover
    return ui.card(
        ui.card_header(
            column_config_icon, ui.output_text("group_card_header", inline=True)
        ),
        ui.output_ui("group_keys_ui"),
    )


def _clean(text: str) -> list[str]:
    """
    >>> _clean("\\n\\n before\\n \\nand, after \\n\\n")
    ['before', 'and', 'after']

    """
    return [
        clean_line for line in re.split(r"[\n,]", text) if (clean_line := line.strip())
    ]


@module.server
def group_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    name: ColumnName,
    group_keys: reactive.Value[dict[ColumnName, list[str]]],
):  # pragma: no cover

    @reactive.effect
    @reactive.event(input.group_keys)
    def _set_group_keys():
        group_keys.set({**group_keys(), name: _clean(input.group_keys())})

    @render.text
    def group_card_header():
        return f"{name} values"

    @render.ui
    def group_keys_ui():
        return [
            ui.markdown(
                f"""
                If known, provide all values for `{name}`,
                one per line. If the values are not known,
                those which occur only a small number of times
                will be excluded from the results,
                because their inclusion would compromise privacy.
                """
            ),
            ui.input_text_area(
                "group_keys",
                only_for_screenreader(f"Known values for `{name}`, one per line"),
                "\n".join(group_keys().get(name, "")),
                rows=5,
                update_on="blur",
            ),
        ]
