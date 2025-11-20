from shiny import Inputs, Outputs, Session, module, render, ui

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


@module.server
def group_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    # public_csv_path: str,
    # product: reactive.Value[Product],
    name: ColumnName,
    # contributions: reactive.Value[int],
    # contributions_entity: reactive.Value[str],
    # epsilon: reactive.Value[float],
    # row_count: int,
    # groups: reactive.Value[list[ColumnName]],
    # analysis_types: reactive.Value[dict[ColumnName, AnalysisName]],
    # analysis_errors: reactive.Value[dict[ColumnName, bool]],
    # lower_bounds: reactive.Value[dict[ColumnName, float]],
    # upper_bounds: reactive.Value[dict[ColumnName, float]],
    # bin_counts: reactive.Value[dict[ColumnName, int]],
    # weights: reactive.Value[dict[ColumnName, str]],
    # is_tutorial_mode: reactive.Value[bool],
    # is_sample_csv: bool,
    # is_single_column: bool,
):  # pragma: no cover

    # @reactive.effect
    # def _set_hidden_inputs():
    #     # TODO: Is isolate still needed?
    #     with reactive.isolate():  # Without isolate, there is an infinite loop.
    # ui.update_numeric("weight", value=int(weights().get(name, default_weight)))

    # @reactive.effect
    # @reactive.event(input.analysis_type)
    # def _set_analysis_type():
    #     analysis_types.set({**analysis_types(), name: input.analysis_type()})

    @render.text
    def group_card_header():
        return name

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
                "",
                rows=5,
            ),
        ]
