from shiny import ui, render, module, reactive, Inputs, Outputs, Session


from dp_wizard.analyses import histogram, mean
from dp_wizard.utils.code_generators import make_column_config_block
from dp_wizard.app.components.outputs import output_code_sample, demo_tooltip, hide_if
from dp_wizard.analyses.histogram.shiny import histogram_ui, histogram_server


default_analysis_type = histogram.name
default_weight = "2"
label_width = "10em"  # Just wide enough so the text isn't trucated.


@module.ui
def column_ui():  # pragma: no cover
    return ui.card(
        ui.card_header(ui.output_text("card_header")),
        ui.input_select(
            "analysis_type",
            None,
            [histogram.name, mean.name],
            width=label_width,
        ),
        ui.output_ui("analysis_config_ui"),
    )


@module.server
def column_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    public_csv_path: str,
    name: str,
    contributions: int,
    epsilon: float,
    row_count: int,
    analysis_types: reactive.Value[dict[str, str]],
    lower_bounds: reactive.Value[dict[str, float]],
    upper_bounds: reactive.Value[dict[str, float]],
    bin_counts: reactive.Value[dict[str, int]],
    weights: reactive.Value[dict[str, str]],
    is_demo: bool,
    is_single_column: bool,
):  # pragma: no cover
    histogram_server(
        name,
        name=name,
        row_count=row_count,
        contributions=contributions,
        epsilon=epsilon,
        weights=weights,
        public_csv_path=public_csv_path,
    )

    @reactive.effect
    def _set_hidden_inputs():
        # TODO: Is isolate still needed?
        with reactive.isolate():  # Without isolate, there is an infinite loop.
            ui.update_numeric("weight", value=int(weights().get(name, default_weight)))

    @reactive.effect
    @reactive.event(input.analysis_type)
    def _set_analysis_type():
        analysis_types.set({**analysis_types(), name: input.analysis_type()})

    @reactive.effect
    @reactive.event(input.lower)
    def _set_lower():
        lower_bounds.set({**lower_bounds(), name: float(input.lower())})

    @reactive.effect
    @reactive.event(input.upper)
    def _set_upper():
        upper_bounds.set({**upper_bounds(), name: float(input.upper())})

    @reactive.effect
    @reactive.event(input.bins)
    def _set_bins():
        bin_counts.set({**bin_counts(), name: int(input.bins())})

    @reactive.effect
    @reactive.event(input.weight)
    def _set_weight():
        weights.set({**weights(), name: input.weight()})

    @render.text
    def card_header():
        return name

    @render.ui
    def analysis_config_ui():
        col_widths = {
            # Controls stay roughly a constant width;
            # Graph expands to fill space.
            "sm": [4, 8],
            "md": [3, 9],
            "lg": [2, 10],
        }
        match input.analysis_type():
            case histogram.name:
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
                        ui.input_numeric(
                            "bins",
                            ["Bins", ui.output_ui("bins_tooltip_ui")],
                            bin_counts().get(name, 10),
                            width=label_width,
                        ),
                        ui.output_ui("optional_weight_ui"),
                    ],
                    histogram_ui(name),
                    col_widths=col_widths,  # type: ignore
                )
            case mean.name:
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
    def bins_tooltip_ui():
        return demo_tooltip(
            is_demo,
            """
            Different statistics can be measured with DP.
            This tool provides a histogram. If you increase the number of bins,
            you'll see that each individual bin becomes noisier to provide
            the same overall privacy guarantee. For this example, give
            "class_year" 4 bins and "grade" 5 bins.
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

    @render.ui
    def weight_tooltip_ui():
        return demo_tooltip(
            is_demo,
            """
            You have a finite privacy budget, but you can choose
            how to allocate it. For simplicity, we limit the options here,
            but when using the library you can fine tune this.
            """,
        )

    @render.code
    def column_code():
        return make_column_config_block(
            name=name,
            analysis_type=input.analysis_type(),
            lower_bound=float(input.lower()),
            upper_bound=float(input.upper()),
            bin_count=int(input.bins()),
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
