from dp_wizard.utils.code_generators._template import Template


name = "Histogram"


def make_query(code_gen, identifier, accuracy_name, stats_name):
    return (
        Template("histogram_query")
        .fill_values(
            BIN_NAME=f"{identifier}_bin",
            GROUP_NAMES=code_gen.groups,
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
        Template(f"histogram_{code_gen.root_template}_output")
        .fill_values(
            COLUMN_NAME=column_name,
            GROUP_NAMES=code_gen.groups,
        )
        .fill_expressions(
            ACCURACY_NAME=accuracy_name,
            HISTOGRAM_NAME=stats_name,
            CONFIDENCE_NOTE=code_gen._make_confidence_note(),
        )
        .finish()
    )
