from dp_wizard.utils.code_template import Template


name = "Histogram"
blurb_md = """
Choosing a smaller number of bins will conserve your
privacy budget and give you more accurate counts.
While the bins are evenly spaced in DP Wizard,
the OpenDP library lets you pick arbitrary cut points.
"""
input_names = [
    "lower_bound_input",
    "upper_bound_input",
    "bin_count_input",
]


def has_bins():
    return True


def make_query(code_gen, identifier, accuracy_name, stats_name):
    return (
        Template("histogram_query", __file__)
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
        Template(f"histogram_{code_gen.root_template}_output", __file__)
        .fill_values(
            COLUMN_NAME=column_name,
            GROUP_NAMES=code_gen.analysis_plan.groups,
        )
        .fill_expressions(
            ACCURACY_NAME=accuracy_name,
            HISTOGRAM_NAME=stats_name,
            CONFIDENCE_NOTE=code_gen._make_confidence_note(),
        )
        .finish()
    )


def make_report_kv(name, confidence, identifier):
    return (
        Template("histogram_report_kv", __file__)
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
    from dp_wizard.utils.code_generators import snake_case

    snake_name = snake_case(column_name)
    return (
        Template("histogram_expr", __file__)
        .fill_expressions(
            CUT_LIST_NAME=f"{snake_name}_cut_points",
            BIN_EXPR_NAME=f"{snake_name}_bin_expr",
        )
        .fill_values(
            LOWER_BOUND=lower_bound,
            UPPER_BOUND=upper_bound,
            BIN_COUNT=bin_count,
            COLUMN_NAME=column_name,
            BIN_COLUMN_NAME=f"{snake_name}_bin",
        )
        .finish()
    )
