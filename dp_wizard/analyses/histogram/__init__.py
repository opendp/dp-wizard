from shiny import ui


name = "Histogram"


def analysis_config_ui(lower_bounds, upper_bounds, bin_counts, label_width, col_widths):
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
        ui.output_ui("histogram_preview_ui"),
        col_widths=col_widths,  # type: ignore
    )
