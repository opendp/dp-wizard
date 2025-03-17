from shiny import ui, render, module, reactive, Inputs, Outputs, Session
from dp_wizard.app.components.outputs import demo_tooltip, hide_if, output_code_sample
from dp_wizard.analyses.common import (
    default_weight,
    label_width,
    col_widths,
    weight_choices,
    bounds_tooltip_text,
)


@module.ui
def mean_ui():  # pragma: no cover
    return ui.output_ui("mean_inputs_preview_ui")


@module.server
def mean_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    name: str,
    lower_bounds: reactive.Value[dict[str, float]],
    upper_bounds: reactive.Value[dict[str, float]],
    is_single_column: bool,
    is_demo: bool,
):  # pragma: no cover
    @render.ui
    def mean_inputs_preview_ui():
        return ui.layout_columns(
            [
                ui.input_numeric(
                    "lower",
                    ["Lower", ui.output_ui("bounds_tooltip_ui")],
                    lower_bounds().get(name, 0),
                    width=label_width,
                ),
                ui.input_numeric(
                    "upper",
                    "Upper",
                    upper_bounds().get(name, 10),
                    width=label_width,
                ),
                ui.output_ui("optional_weight_ui"),
            ],
            ui.output_ui("mean_preview_ui"),
            col_widths=col_widths,  # type: ignore
        )

    @render.ui
    def mean_preview_ui():
        return [
            ui.p(
                """
                Since the mean is just a single number,
                there is not a preview visualization.
                """
            ),
            output_code_sample("Column Definition", "column_code"),
        ]

    @render.ui
    def bounds_tooltip_ui():
        return demo_tooltip(
            is_demo,
            bounds_tooltip_text,
        )

    @render.ui
    def optional_weight_ui():
        return hide_if(
            is_single_column,
            ui.input_select(
                "weight",
                ["Weight", ui.output_ui("weight_tooltip_ui")],
                choices=weight_choices,
                selected=default_weight,
                width=label_width,
            ),
        )
