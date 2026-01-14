from logging import info

import polars as pl
from htmltools.tags import details, summary
from shiny import Inputs, Outputs, Session, module, reactive, render, ui
from shiny.types import SilentException

from dp_wizard.shiny.components.icons import (
    column_config_icon,
)
from dp_wizard.shiny.components.outputs import (
    code_sample,
    col_widths,
    hide_if,
    only_for_screenreader,
    tutorial_box,
    warning_md_box,
)
from dp_wizard.types import ColumnName, Product, StatisticName, Weight
from dp_wizard.utils.code_generators import make_column_config_block
from dp_wizard.utils.code_generators.analyses import (
    get_statistic_by_name,
    histogram,
    mean,
    median,
)
from dp_wizard.utils.constraints import MAX_BOUND, MIN_BOUND
from dp_wizard.utils.dp_helper import confidence, make_accuracy_histogram
from dp_wizard.utils.mock_data import ColumnDef, mock_data
from dp_wizard.utils.shared.plots import plot_bars

default_statistic_name = histogram.name
label_width = "10em"  # Just wide enough so the text isn't trucated.


def get_float_error(number_str) -> str | None:
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
    >>> get_float_error('1_000_000_000_001')
    'should not be greater than 100,000,000,000'
    >>> get_float_error('-1_000_000_000_001')
    'should not be less than -100,000,000,000'
    """
    if number_str is None or number_str == "":
        return "is required"
    try:
        number = int(float(number_str))
    except (TypeError, ValueError, OverflowError):
        return "should be a number"
    if number > MAX_BOUND:
        return f"should not be greater than {MAX_BOUND:,}"
    if number < MIN_BOUND:
        return f"should not be less than {MIN_BOUND:,}"
    return None


def get_bound_errors(lower_bound, upper_bound) -> list[str]:
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


def get_bin_errors(count) -> list[str]:
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
    >>> get_bin_errors("101")
    ['Number should be less than 100, just to keep computation from running too long.']
    """
    if error := get_float_error(count):
        return [f"Number {error}."]
    count = int(float(count))
    if count <= 0:
        return ["Number should be a positive integer."]
    max_count = 100
    if count > max_count:
        return [
            f"Number should be less than {max_count}, "
            "just to keep computation from running too long."
        ]
    return []


@module.ui
def column_ui():  # pragma: no cover
    return ui.card(
        ui.card_header(
            column_config_icon, ui.output_text("column_card_header", inline=True)
        ),
        ui.output_ui("statistic_name_ui"),
        ui.output_ui("statistic_config_ui"),
    )


@module.server
def column_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    public_csv_path: str,
    product: reactive.Value[Product],
    name: ColumnName,
    contributions: reactive.Value[int],
    contributions_entity: reactive.Value[str],
    epsilon: reactive.Value[float],
    row_count: int,
    groups: reactive.Value[list[ColumnName]],
    statistic_names: reactive.Value[dict[ColumnName, StatisticName]],
    analysis_errors: reactive.Value[dict[ColumnName, bool]],
    lower_bounds: reactive.Value[dict[ColumnName, float]],
    upper_bounds: reactive.Value[dict[ColumnName, float]],
    bin_counts: reactive.Value[dict[ColumnName, int]],
    weights: reactive.Value[dict[ColumnName, Weight]],
    is_tutorial_mode: reactive.Value[bool],
    is_sample_csv: bool,
    is_single_column: bool,
):  # pragma: no cover
    @reactive.effect
    def _set_hidden_inputs():
        # TODO: Is isolate still needed?
        with reactive.isolate():  # Without isolate, there is an infinite loop.
            ui.update_numeric(
                "weight",
                value=int(weights().get(name, Weight.DEFAULT).value),
            )

    @reactive.effect
    @reactive.event(input.statistic_name)
    def _set_statistic_name():
        statistic_names.set({**statistic_names(), name: input.statistic_name()})

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
        weights.set({**weights(), name: Weight(input.weight())})

    @reactive.calc()
    def accuracy_histogram():
        lower_x = float(input.lower_bound())
        upper_x = float(input.upper_bound())
        bin_count = int(input.bins())
        weight = float(input.weight())
        weights_sum = sum(float(weight.value) for weight in weights().values())
        info(f"Weight ratio for {name}: {weight}/{weights_sum}")
        if weights_sum == 0:
            # This function is triggered when column is removed;
            # Exit early to avoid divide-by-zero.
            raise SilentException("weights_sum == 0")

        # Mock data only depends on lower and upper bounds, so it could be cached,
        # but I'd guess this is dominated by the DP operations,
        # so not worth optimizing.
        lf = (
            pl.scan_csv(public_csv_path, ignore_errors=True)
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
    def column_card_header():
        groups_str = ", ".join(groups())
        if not groups_str:
            return name
        return f"{name} (grouped by {groups_str})"

    @render.ui
    def statistic_name_ui():
        statistic_name = statistic_names().get(name, histogram.name)
        blurb_md = get_statistic_by_name(statistic_name).blurb_md
        return hide_if(
            product() != Product.STATISTICS,
            (
                ui.layout_columns(
                    ui.input_select(
                        "statistic_name",
                        only_for_screenreader("Type of statistic"),
                        [histogram.name, mean.name, median.name],
                        width=label_width,
                        selected=statistic_name,
                    ),
                    ui.markdown(blurb_md),
                    col_widths=col_widths,  # type: ignore
                ),
            ),
        )

    @render.ui
    def statistic_config_ui():
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
                tutorial_box(
                    is_tutorial_mode(),
                    """
                    Interpreting differential privacy strictly,
                    we should try never to look directly at the data,
                    not even to set bounds! This can be hard.
                    """,
                    is_sample_csv,
                    """
                    Given what we know _a priori_ about grading scales,
                    you could limit `grade` to values between 0 and 100.
                    """,
                    responsive=False,
                ),
            ]

        def bin_count_input():
            return [
                ui.input_numeric(
                    "bins",
                    "Number of Bins",
                    bin_counts().get(name, 10),
                    width=label_width,
                ),
                tutorial_box(
                    is_tutorial_mode(),
                    """
                    If you decrease the number of bins,
                    you'll see that each individual bin becomes
                    less noisy.
                    """,
                    responsive=False,
                ),
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

        # Preserve the user's choices behind the scenes,
        # but only show mean and median column UI if actually calculating stats:
        # otherwise show the histogram UI.
        statistic_name = (
            input.statistic_name()
            if product() == Product.STATISTICS
            else histogram.name
        )

        # Had trouble with locals() inside comprehension in Python 3.10.
        # Not sure if this is the exact issue:
        # https://github.com/python/cpython/issues/105256

        # Fix is just to keep it outside the comprehension.
        local_variables = locals()
        input_names = get_statistic_by_name(statistic_name).input_names
        input_functions = [local_variables[input_name] for input_name in input_names]
        with reactive.isolate():
            inputs = [input_function() for input_function in input_functions] + [
                ui.output_ui("optional_weight_ui")
            ]

        return ui.layout_columns(
            inputs,
            ui.output_ui(f"{statistic_name.lower()}_preview_ui"),
            col_widths=col_widths,  # type: ignore
        )

    @render.ui
    def optional_weight_ui():
        return hide_if(
            is_single_column,
            [
                ui.input_select(
                    "weight",
                    "Weight",
                    choices={w.value: str(w) for w in Weight},
                    selected=Weight.DEFAULT.value,
                    width=label_width,
                ),
                tutorial_box(
                    is_tutorial_mode(),
                    """
                    You have a finite privacy budget, but you can choose
                    how to allocate it. For simplicity, we limit the options here,
                    but when using the library you can fine tune this.
                    """,
                    responsive=False,
                ),
            ],
        )

    @reactive.calc
    def error_md_calc():
        bound_errors = get_bound_errors(input.lower_bound(), input.upper_bound())

        return "\n".join(
            f"- {error}" for error in bound_errors + get_bin_errors(input.bins())
        )

    @reactive.effect
    def set_analysis_errors():
        with reactive.isolate():
            prev_analysis_errors = analysis_errors()
        analysis_errors.set({**prev_analysis_errors, name: bool(error_md_calc())})

    @render.ui
    def column_python_ui():
        return code_sample(
            "Column Configuration",
            make_column_config_block(
                name=name,
                statistic_name=input.statistic_name(),
                lower_bound=float(input.lower_bound()),
                upper_bound=float(input.upper_bound()),
                bin_count=int(input.bins()),
            ),
        )

    @render.ui
    def histogram_preview_ui():
        if error_md := error_md_calc():
            return warning_md_box(error_md)
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
                ui.output_ui("column_python_ui"),
            ),
        ]

    def stat_preview_ui():
        if error_md := error_md_calc():
            return warning_md_box(error_md)
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
            ui.output_ui("column_python_ui"),
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
        title_name = (
            name
            if public_csv_path
            else f"Simulated {name} (assuming a normal distribution)"
        )

        contributions_int = contributions()
        s = "s" if contributions_int > 1 else ""
        title_contributions = (
            f"{contributions_int} contribution{s} / {contributions_entity()}"
        )

        accuracy, histogram = accuracy_histogram()
        return plot_bars(
            histogram,
            error=accuracy,
            title=f"{title_name}, {title_contributions}",
        )
