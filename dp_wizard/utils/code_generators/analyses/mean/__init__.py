from dp_wizard.utils.code_template import Template


name = "Mean"
blurb_md = """
Choosing tighter bounds will mean less noise added
to the statistics, but if you pick bounds that
are too tight, you'll miss the contributions of
outliers.
"""
input_names = [
    "lower_bound_input",
    "upper_bound_input",
]


def has_bins():
    return False


def make_query(code_gen, identifier, accuracy_name, stats_name):
    return (
        Template("mean_query", __file__)
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
        Template(f"mean_{code_gen.root_template}_output", __file__)
        .fill_expressions(
            COLUMN_NAME=column_name,
            STATS_NAME=stats_name,
        )
        .finish()
    )


def make_report_kv(name, confidence, identifier):
    return (
        Template("mean_report_kv", __file__)
        .fill_values(
            NAME=name,
        )
        .fill_expressions(
            IDENTIFIER_STATS=f"{identifier}_stats",
        )
        .finish()
    )


def make_column_config_block(column_name, lower_bound, upper_bound, bin_count):
    from dp_wizard.utils.code_generators import snake_case

    snake_name = snake_case(column_name)
    return (
        Template("mean_expr", __file__)
        .fill_expressions(
            EXPR_NAME=f"{snake_name}_expr",
        )
        .fill_values(
            COLUMN_NAME=column_name,
            LOWER_BOUND=lower_bound,
            UPPER_BOUND=upper_bound,
        )
        .finish()
    )
