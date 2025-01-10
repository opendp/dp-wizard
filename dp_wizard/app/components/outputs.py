from htmltools.tags import details, summary
from shiny import ui
from faicons import icon_svg


def output_code_sample(title: str, name_of_render_function: str):
    return details(
        summary(f"Code sample: {title}"),
        ui.output_code(name_of_render_function),
    )


def demo_tooltip(is_demo: bool, text: str):  # pragma: no cover
    if is_demo:
        return ui.tooltip(
            icon_svg("circle-question"),
            text,
            placement="right",
        )


def hide_if(condition: bool, el):  # pragma: no cover
    display = "none" if condition else "block"
    return ui.div(el, style=f"display: {display};")


def info_box(content):  # pragma: no cover
    return ui.div(content, class_="alert alert-info", role="alert")
