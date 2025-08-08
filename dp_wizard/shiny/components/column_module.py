from logging import info

from htmltools.tags import details, summary
from shiny import ui, render, module, reactive, Inputs, Outputs, Session
from shiny.types import SilentException
import polars as pl

from dp_wizard.utils.code_generators.analyses import (
    histogram,
    mean,
    median,
    count,
    get_analysis_by_name,
)
from dp_wizard.utils.dp_helper import make_accuracy_histogram
from dp_wizard.utils.shared import plot_bars
from dp_wizard.utils.code_generators import make_column_config_block
from dp_wizard.shiny.components.outputs import (
    output_code_sample,
    demo_help,
    info_md_box,
    hide_if,
    col_widths,
)
from dp_wizard.utils.dp_helper import confidence
from dp_wizard.utils.mock_data import mock_data, ColumnDef


default_analysis_type = histogram.name
default_weight = "2"
label_width = "10em"  # Just wide enough so the text isn't trucated.


def get_float_error(number_str):
    """
    If the inputs are numeric, I think shiny converts
    any strings that can't be parsed to numbers into None,
    so the "should be a number" errors may not be seen in practice.
    >>> get_float_error('0')
    >>> get_float_error(None)
    'is required'
    >>> get_float_error('')
    'is required'
    >>> get_float_error('1.1')
    >>> get_float_error('nan')
    'should be a number'
    >>> get_float_error('inf')
    'should be a number'
    """
    if number_str is None or number_str == "":
        return "is required"
    try:
        int(float(number_str))
    except (TypeError, ValueError, OverflowError):
        return "should be a number"
    return None


def get_bound_errors(lower_bound, upper_bound):
    """
    >>> get_bound_errors(1, 2)
    []
    >>> get_bound_errors('abc', 'xyz')
    ['Lower bound should be a number.', 'Upper bound should be a number.']
    >>> get_bound_errors(1, None)
    ['Upper bound is required.']
    >>> get_bound_errors(1, 0)
    ['Lower bound should be less than upper bound.']
    """
    messages = []
    if error := get_float_error(lower_bound):
        messages.append(f"Lower bound {error}.")
    if error := get_float_error(upper_bound):
        messages.append(f"Upper bound {error}.")
    if not messages:
        if not (float(lower_bound) < float(upper_bound)):
            messages.append("Lower bound should be less than upper bound.")
    return messages


def get_bin_errors(count):
    """
    This function might be applied to either histogram bin counts,
    or median candidate counts, so the wording is a little vague.

    >>> get_bin_errors("5")
    []
    >>> get_bin_errors(None)
    ['Number is required.']
    >>> get_bin_errors("abc")
    ['Number should be a number.']
    >>> get_bin_errors("-1")
    ['Number should be a positive integer.']
    >>> get_bin_errors("1001")
    ['Number should be less than 1000, just to keep computation from running too long.']
    """
    if error := get_float_error(count):
        return [f"Number {error}."]
    count = int(float(count))
    if count <= 0:
        return ["Number should be a positive integer."]
    if count > 1000:
        return [
            "Number should be less than 1000, "
            "just to keep computation from running too long."
        ]
    return []


def error_md_ui(markdown):  # pragma: no cover
    return info_md_box(markdown)


@module.ui
def column_ui():  # pragma: no cover
    return ui.card(
        ui.card_header(ui.output_text("card_header")),
        ui.layout_columns(
            ui.input_select(
                "analysis_type",
                None,
                [histogram.name, mean.name, median.name, count.name],
                width=label_width,
            ),
            ui.output_ui("analysis_info_ui"),
            col_widths=col_widths,  # type: ignore
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
    contributions: reactive.Value[int],
    epsilon: reactive.Value[float],
    row_count: int,
    groups: reactive.Value[list[str]],
    analysis_types: reactive.Value[dict[str, str]],
    analysis_errors: reactive.Value[dict[str, bool]],
    lower_bounds: reactive.Value[dict[str, float]],
    upper_bounds: reactive.Value[dict[str, float]],
    bin_counts: reactive.Value[dict[str, int]],
    weights: reactive.Value[dict[str, str]],
    is_demo: bool,
    is_single_column: bool,
):  # pragma: no cover
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
    @reactive.event(input.lower_bound)
    def _set_lower_bound():
        try:
            value = float(input.lower_bound())
        except ValueError:
            raise SilentException()
        lower_bounds.set({**lower_bounds(), name: value})

    @reactive.effect
    @reactive.event(input.upper_bound)
    def _set_upper_bound():
        try:
            value = float(input.upper_bound())
        except ValueError:
            raise SilentException()
        upper_bounds.set({**upper_bounds(), name: value})

    @reactive.effect
    @reactive.event(input.bins)
    def _set_bins():
        try:
            value = int(input.bins())
        except ValueError:
            raise SilentException()
        bin_counts.set({**bin_counts(), name: value})

    @reactive.effect
    @reactive.event(input.weight)
    def _set_weight():
        weights.set({**weights(), name: input.weight()})

    @reactive.calc()
    def accuracy_histogram():
        lower_x = float(input.lower_bound())
        upper_x = float(input.upper_bound())
        bin_count = int(input.bins())
        weight = float(input.weight())
        weights_sum = sum(float(weight) for weight in weights().values())
        info(f"Weight ratio for {name}: {weight}/{weights_sum}")
        if weights_sum == 0:
            # This function is triggered when column is removed;
            # Exit early to avoid divide-by-zero.
            raise SilentException("weights_sum == 0")

        # Mock data only depends on lower and upper bounds, so it could be cached,
        # but I'd guess this is dominated by the DP operations,
        # so not worth optimizing.
        lf = (
            pl.scan_csv(public_csv_path)
            if public_csv_path
            else pl.LazyFrame(
                mock_data({name: ColumnDef(lower_x, upper_x)}, row_count=row_count)
            )
        )
        return make_accuracy_histogram(
            lf=lf,
            column_name=name,
            row_count=row_count,
            lower_bound=lower_x,
            upper_bound=upper_x,
            bin_count=bin_count,
            contributions=contributions(),
            weighted_epsilon=epsilon() * weight / weights_sum,
        )

    @render.text
    def card_header():
        groups_str = ", ".join(groups())
        if not groups_str:
            return name
        return f"{name} (grouped by {groups_str})"

    @render.ui
    def analysis_info_ui():
        blurb_md = get_analysis_by_name(input.analysis_type()).blurb_md
        return ui.markdown(blurb_md)

    @render.ui
    def analysis_config_ui():
        def lower_bound_input():
            return ui.input_text(
                "lower_bound",
                "Lower Bound",
                str(lower_bounds().get(name, "")),
                width=label_width,
            )

        def upper_bound_input():
            return [
                ui.input_text(
                    "upper_bound",
                    "Upper Bound",
                    str(upper_bounds().get(name, "")),
                    width=label_width,
                ),
                ui.output_ui("bounds_tooltip_ui"),
            ]

        def bin_count_input():
            return [
                ui.input_numeric(
                    "bins",
                    "Number of Bins",
                    bin_counts().get(name, 10),
                    width=label_width,
                ),
                ui.output_ui("bins_tooltip_ui"),
            ]

        def candidate_count_input():
            # Just change the user-visible label,
            # but still call it "bin" internally.
            # Less new code; pretty much the same thing.
            return ui.input_numeric(
                "bins",
                "Number of Candidates",
                bin_counts().get(name, 0),
                width=label_width,
            )

        name = input.analysis_type()

        # Had trouble with locals() inside comprehension in Python 3.10.
        # Not sure if this is the exact issue:
        # https://github.com/python/cpython/issues/105256

        # Fix is just to keep it outside the comprehension.
        local_variables = locals()
        input_names = get_analysis_by_name(name).input_names
        input_functions = [local_variables[input_name] for input_name in input_names]
        with reactive.isolate():
            inputs = [input_function() for input_function in input_functions] + [
                ui.output_ui("optional_weight_ui")
            ]

        return ui.layout_columns(
            inputs,
            ui.output_ui(f"{name.lower()}_preview_ui"),
            col_widths=col_widths,  # type: ignore
        )

    @render.ui
    def bounds_tooltip_ui():
        return demo_help(
            is_demo,
            """
            Don't look at the data when estimating the bounds!
            In this case, we could limit "grade" to values between 50 and 100.
            """,
            responsive=False,
        )

    @render.ui
    def bins_tooltip_ui():
        return demo_help(
            is_demo,
            """
            If you increase the number of bins,
            you'll see that each individual bin becomes noisier to provide
            the same overall privacy guarantee.
            Give "grade" 5 bins.
            """,
            responsive=False,
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
        return demo_help(
            is_demo,
            """
            You have a finite privacy budget, but you can choose
            how to allocate it. For simplicity, we limit the options here,
            but when using the library you can fine tune this.
            """,
        )

    @reactive.calc
    def error_md_calc():
        return "\n".join(
            f"- {error}"
            for error in get_bound_errors(input.lower_bound(), input.upper_bound())
            + get_bin_errors(input.bins())
        )

    @reactive.effect
    def set_analysis_errors():
        with reactive.isolate():
            prev_analysis_errors = analysis_errors()
        analysis_errors.set({**prev_analysis_errors, name: bool(error_md_calc())})

    @render.code
    def column_code():
        return make_column_config_block(
            name=name,
            analysis_type=input.analysis_type(),
            lower_bound=float(input.lower_bound()),
            upper_bound=float(input.upper_bound()),
            bin_count=int(input.bins()),
        )

    @render.ui
    def histogram_preview_ui():
        if error_md := error_md_calc():
            return error_md_ui(error_md)
        accuracy, histogram = accuracy_histogram()
        return [
            ui.output_plot("histogram_preview_plot", height="300px"),
            ui.layout_columns(
                ui.markdown(
                    f"The {confidence:.0%} confidence interval is ±{accuracy:.3g}."
                ),
                details(
                    summary("Data Table"),
                    ui.output_data_frame("data_frame"),
                ),
                output_code_sample("Column Definition", "column_code"),
            ),
        ]

    def stat_preview_ui():
        if error_md := error_md_calc():
            return error_md_ui(error_md)
        optional_grouping_message = (
            # TODO: Show bar chart with fake groups?
            # https://github.com/opendp/dp-wizard/issues/493#issuecomment-3000774143
            (
                """
                Because the data is grouped, the final release will include a bar chart,
                where each bar is the value of the statistic for one group.
                """
            )
            if groups()
            # TODO: Show a bar, even if it's just one bar? Not sure about this.
            # https://github.com/opendp/dp-wizard/issues/518
            else ""
        )
        return [
            ui.p(
                f"""
                Since this stat is just a single number,
                there is not a preview visualization.
                {optional_grouping_message}
                """
            ),
            output_code_sample("Column Definition", "column_code"),
        ]

    @render.ui
    def mean_preview_ui():
        return stat_preview_ui()

    @render.ui
    def median_preview_ui():
        return stat_preview_ui()

    @render.ui
    def count_preview_ui():
        return stat_preview_ui()

    @render.data_frame
    def data_frame():
        accuracy, histogram = accuracy_histogram()
        return render.DataGrid(histogram)

    @render.plot
    def histogram_preview_plot():
        accuracy, histogram = accuracy_histogram()
        contributions_int = contributions()
        s = "s" if contributions_int > 1 else ""
        title = ", ".join(
            [
                name if public_csv_path else f"Simulated {name}: normal distribution",
                f"{contributions_int} contribution{s} / individual",
            ]
        )
        return plot_bars(
            histogram,
            error=accuracy,
            cutoff=0,  # TODO
            title=title,
        )
