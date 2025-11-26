import re

import polars as pl
from shiny import Inputs, Outputs, Session, module, reactive, render, ui

from dp_wizard.shiny.components.icons import column_config_icon
from dp_wizard.shiny.components.outputs import only_for_screenreader
from dp_wizard.types import ColumnName


@module.ui
def group_ui():  # pragma: no cover
    return ui.card(
        ui.card_header(
            column_config_icon, ui.output_text("group_card_header", inline=True)
        ),
        ui.output_ui("group_keys_ui"),
    )


def _clean(text: str, target_type: pl.DataType) -> list[str | float]:
    """
    >>> _clean("\\n\\n before\\n \\nand, after \\n\\n", pl.String)
    ['before', 'and', 'after']

    >>> _clean("-1,0,1,3.14159", pl.Int32)
    [-1, 0, 1]

    >>> _clean("-1.1,0,1.1,foobar", pl.Float32)
    [-1.1, 0.0, 1.1]
    """
    if target_type.is_float():
        convert = float
    elif target_type.is_integer():
        convert = int
    elif target_type == pl.String:
        convert = str
    else:
        raise Exception(f"Unexpected type: {target_type}")

    def safe_convert(value):
        try:
            new = convert(value)
        except ValueError:
            new = None
        return new

    clean_lines = [
        clean_line for line in re.split(r"[\n,]", text) if (clean_line := line.strip())
    ]

    converted_lines = [
        converted_line
        for line in clean_lines
        if (converted_line := safe_convert(line)) is not None
    ]
    return converted_lines


@module.server
def group_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    name: ColumnName,
    group_keys: reactive.Value[dict[ColumnName, list[str | float]]],
    polars_schema: reactive.Value[pl.Schema],
):  # pragma: no cover

    @reactive.effect
    @reactive.event(input.group_keys)
    def _set_group_keys():
        target_type = polars_schema()[name]
        cleaned = _clean(input.group_keys(), target_type)
        if target_type.is_float():
            cleaned: list[str | float] = [float(n) for n in cleaned]
        elif target_type.is_integer():
            cleaned: list[str | float] = [int(n) for n in cleaned]
        elif target_type != pl.String:
            raise Exception(f"Unexpected type: {target_type}")

        group_keys.set({**group_keys(), name: cleaned})

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
                "\n".join(str(value) for value in group_keys().get(name, [])),
                rows=5,
                update_on="blur",
            ),
        ]
