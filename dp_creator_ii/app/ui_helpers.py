from htmltools.tags import details, summary
from shiny import ui


def output_code_sample(name_of_render_function):
    return details(
        summary("Code sample"),
        ui.output_code(name_of_render_function),
    )
