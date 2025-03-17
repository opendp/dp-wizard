from shiny import ui, render, module, reactive, Inputs, Outputs, Session
from dp_wizard.app.components.outputs import demo_tooltip, hide_if, output_code_sample


default_weight = "2"
label_width = "10em"  # Just wide enough so the text isn't trucated.
col_widths = {
    # Controls stay roughly a constant width;
    # Graph expands to fill space.
    "sm": [4, 8],
    "md": [3, 9],
    "lg": [2, 10],
}


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
        # accuracy, histogram = accuracy_histogram()
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
            """
            DP requires that we limit the sensitivity to the contributions
            of any individual. To do this, we need an estimate of the lower
            and upper bounds for each variable. We should not look at the
            data when estimating the bounds! In this case, we could imagine
            that "class year" would vary between 1 and 4, and we could limit
            "grade" to values between 50 and 100.
            """,
        )

    @render.ui
    def optional_weight_ui():
        return hide_if(
            is_single_column,
            ui.input_select(
                "weight",
                ["Weight", ui.output_ui("weight_tooltip_ui")],
                choices={
                    "1": "Less accurate",
                    default_weight: "Default",
                    "4": "More accurate",
                },
                selected=default_weight,
                width=label_width,
            ),
        )
