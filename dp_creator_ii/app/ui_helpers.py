from htmltools.tags import details, pre, summary
from shiny import ui


def output_code_sample(name_of_render_function):
    return details(
        summary("Code sample"),
        pre(
            ui.output_text(name_of_render_function),
        ),
    )
