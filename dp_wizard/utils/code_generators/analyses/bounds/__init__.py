from dp_wizard_templates.code_template import Template

from dp_wizard import opendp_version
from dp_wizard.types import ColumnIdentifier, StatisticName
from dp_wizard.utils.code_generators.abstract_generator import get_template_root

name = StatisticName("Bounds")
blurb_md = """
DB statistics require reasonable bounds or candidate values,
and with a new dataset this information may just not be available.
One strategy is to split the analysis into steps,
and first make a release with exponentially wide bins,
and then use that information to set bounds for the desired statistics.
"""
input_names = [
    "upper_bound_input",
]


root = get_template_root(__file__)


def make_query(code_gen, identifier, accuracy_name, stats_name):
    import polars as pl

    def template(BIN_NAME, GROUP_NAMES, stats_context, confidence):
        groups = [BIN_NAME] + GROUP_NAMES
        QUERY_NAME = (
            stats_context.query().group_by(groups).agg(pl.len().dp.noise().alias("count"))  # type: ignore
        )
        ACCURACY_NAME = QUERY_NAME.summarize(alpha=1 - confidence)[  # noqa: F841
            "accuracy"
        ].item()
        STATS_NAME = QUERY_NAME.release().collect()
        STATS_NAME  # type: ignore

    return (
        Template(template)
        .fill_values(
            BIN_NAME=f"{identifier}_bin",
            GROUP_NAMES=code_gen.analysis_plan.groups,
        )
        .fill_expressions(
            QUERY_NAME=f"{identifier}_query",
            ACCURACY_NAME=accuracy_name,
            STATS_NAME=stats_name,
        )
        .finish()
    )


def make_output(code_gen, column_name, accuracy_name, stats_name):
    return (
        Template(f"bounds_{code_gen._get_notebook_or_script()}_output", root)
        .fill_values(
            COLUMN_NAME=column_name,
            GROUP_NAMES=code_gen.analysis_plan.groups,
        )
        .fill_expressions(
            ACCURACY_NAME=accuracy_name,
            bounds_NAME=stats_name,
            CONFIDENCE_NOTE=code_gen._make_confidence_note(),
        )
        .finish()
    )


def make_plot_note():
    return (
        "`None` values above may indicate strings "
        "which could not be converted to numbers."
    )


def make_report_kv(name, confidence, identifier):
    return (
        Template("bounds_report_kv", root)
        .fill_values(
            NAME=name,
            CONFIDENCE=confidence,
        )
        .fill_expressions(
            IDENTIFIER_STATS=f"{identifier}_stats",
            IDENTIFIER_ACCURACY=f"{identifier}_accuracy",
        )
        .finish()
    )


def make_column_config_block(column_name, lower_bound, upper_bound, bin_count):
    identifier = ColumnIdentifier(column_name)
    return (
        Template("bounds_expr", root)
        .fill_expressions(
            CUT_LIST_NAME=f"{identifier}_cut_points",
            BIN_EXPR_NAME=f"{identifier}_bin_expr",
            OPENDP_V_VERSION=f"v{opendp_version}",
        )
        .fill_values(
            EXTREME=upper_bound,
            COLUMN_NAME=column_name,
            BIN_COLUMN_NAME=f"{identifier}_bin",
        )
        .finish()
    )
