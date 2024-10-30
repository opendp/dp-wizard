from htmltools.tags import details, summary
from shiny import ui
from faicons import icon_svg


def output_code_sample(name_of_render_function):
    return details(
        summary("Code sample"),
        ui.output_code(name_of_render_function),
    )


def demo_tooltip(is_demo, text):
    if is_demo:
        return ui.tooltip(
            icon_svg("circle-question"),
            text,
            placement="right",
        )
