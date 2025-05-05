from htmltools.tags import details, summary
from shiny import ui
from faicons import icon_svg


def output_code_sample(title, name_of_render_function: str):
    return details(
        summary(["Code sample: ", title]),
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


def info_md_box(markdown):  # pragma: no cover
    return ui.div(ui.markdown(markdown), class_="alert alert-info", role="alert")


def nav_button(id, label, disabled=False):
    return ui.input_action_button(
        id,
        [ui.tags.span(label, style="padding-right: 1em;"), icon_svg("play")],
        disabled=disabled,
        class_="float-end",
    )
