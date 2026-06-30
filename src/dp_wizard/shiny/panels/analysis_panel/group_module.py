import polars as pl
from shiny import Inputs, Outputs, Session, module, reactive, render, ui

from dp_wizard.shiny.components.icons import column_config_icon
from dp_wizard.shiny.components.outputs import only_for_screenreader
from dp_wizard.types import ColumnName
from dp_wizard.utils.csv_helper import convert_text


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
    name: ColumnName,
    group_keys: reactive.Value[dict[ColumnName, list[str | float]]],
    schema: dict[ColumnName, pl.DataType],
):  # pragma: no cover

    @reactive.effect
    @reactive.event(input.group_keys)
    def _set_group_keys():
        cleaned = convert_text(input.group_keys(), schema[name])
        group_keys.set({**group_keys(), name: cleaned})

    @render.text
    def group_card_header():
        return f"{name} values"

    @render.ui
    def group_keys_ui():
        match pl_datatype := schema[name]:
            case pl.String:
                datatype = "String"
            case pl.Int64:
                datatype = "Integer"
            case pl.Float64:
                datatype = "Floating point"
            case pl.Boolean:
                datatype = "True/False"
            case _:
                datatype = str(pl_datatype)
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
                "\n".join(str(value) for value in group_keys().get(name, [])),
                rows=5,
                update_on="blur",
                placeholder=f"{datatype} values, one per line",
            ),
        ]
