from dp_wizard_templates.code_template import Template

from dp_wizard import get_template_root, opendp_version
from dp_wizard.types import AnalysisName

name = AnalysisName("Median")
blurb_md = """
In DP Wizard the median is picked from evenly spaced
candidates, but the OpenDP library is more flexible.
Because the median isn't based on the addition of noise,
we can't estimate the error as we do with the other
statistics.
"""
input_names = [
    "lower_bound_input",
    "upper_bound_input",
    "candidate_count_input",
]


root = get_template_root(__file__)


def make_query(code_gen, identifier, accuracy_name, stats_name):
    return (  # pragma: no cover
        Template("median_query", root)
        .fill_values(
            GROUP_NAMES=code_gen.analysis_plan.groups,
        )
        .fill_expressions(
            QUERY_NAME=f"{identifier}_query",
            STATS_NAME=stats_name,
            EXPR_NAME=f"{identifier}_expr",
        )
        .finish()
    )


def make_output(code_gen, column_name, accuracy_name, stats_name):
    return (
        Template(f"median_{code_gen._get_notebook_or_script()}_output", root)
        .fill_expressions(
            COLUMN_NAME=column_name,
            STATS_NAME=stats_name,
        )
        .finish()  # pragma: no cover
    )


def make_note():
    return ""


def make_report_kv(name, confidence, identifier):
    return (
        Template("median_report_kv", root)
        .fill_values(
            NAME=name,
        )
        .fill_expressions(
            IDENTIFIER_STATS=f"{identifier}_stats",
        )
        .finish()
    )  # pragma: no cover


def make_column_config_block(column_name, lower_bound, upper_bound, bin_count):
    from dp_wizard.utils.code_generators import snake_case

    snake_name = snake_case(column_name)
    return (
        Template("median_expr", root)
        .fill_expressions(
            EXPR_NAME=f"{snake_name}_expr",
            OPENDP_VERSION=opendp_version,
        )
        .fill_values(
            COLUMN_NAME=column_name,
            LOWER_BOUND=lower_bound,
            UPPER_BOUND=upper_bound,
            BIN_COUNT=bin_count,
        )
        .finish()
    )  # pragma: no cover
