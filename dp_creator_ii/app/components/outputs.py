from htmltools.tags import details, summary
from shiny import ui
from faicons import icon_svg


def output_code_sample(title, name_of_render_function):
    return details(
        summary(f"Code sample: {title}"),
        ui.output_code(name_of_render_function),
    )


def demo_tooltip(is_demo, text):  # pragma: no cover
    if is_demo:
        return ui.tooltip(
            icon_svg("circle-question"),
            text,
            placement="right",
        )
