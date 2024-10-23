from htmltools.tags import details, summary
from shiny import ui


def output_code_sample(title, name_of_render_function):
    return details(
        summary(f"Code sample: {title}"),
        ui.output_code(name_of_render_function),
    )
