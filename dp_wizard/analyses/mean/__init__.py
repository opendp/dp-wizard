from dp_wizard.utils.code_generators._template import Template


name = "Mean"


def make_query(code_gen, identifier, accuracy_name, stats_name):
    return (
        Template("mean_query")
        .fill_values(
            GROUP_NAMES=code_gen.groups,
        )
        .fill_expressions(
            QUERY_NAME=f"{identifier}_query",
            STATS_NAME=stats_name,
            CONFIG_NAME=f"{identifier}_config",
        )
        .finish()
    )


def make_output(code_gen, column_name, accuracy_name, stats_name):
    return Template(f"mean_{code_gen.root_template}_output").finish()
