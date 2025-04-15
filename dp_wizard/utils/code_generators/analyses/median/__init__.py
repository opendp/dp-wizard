from dp_wizard.utils.code_template import Template


name = "Median"


def has_bins():
    return False  # pragma: no cover


def make_query(code_gen, identifier, accuracy_name, stats_name):
    return (  # pragma: no cover
        Template("median_query", __file__)
        .fill_values(
            GROUP_NAMES=code_gen.groups,
        )
        .fill_expressions(
            QUERY_NAME=f"{identifier}_query",
            STATS_NAME=stats_name,
            EXPR_NAME=f"{identifier}_expr",
        )
        .finish()
    )


def make_output(code_gen, column_name, accuracy_name, stats_name):
    return Template(
        f"median_{code_gen.root_template}_output", __file__
    ).finish()  # pragma: no cover


def make_report_kv(name, confidence, identifier):
    return (
        Template("median_report_kv", __file__)
        .fill_values(
            NAME=name,
        )
        .finish()
    )  # pragma: no cover


def make_column_config_block(column_name, lower_bound, upper_bound, bin_count):
    from dp_wizard.utils.code_generators import snake_case

    snake_name = snake_case(column_name)
    return (
        Template("median_expr", __file__)
        .fill_expressions(
            EXPR_NAME=f"{snake_name}_expr",
        )
        .fill_values(
            COLUMN_NAME=column_name,
            LOWER_BOUND=lower_bound,
            UPPER_BOUND=upper_bound,
        )
        .finish()
    )  # pragma: no cover
