from htmltools.tags import details, summary, span, table, tr, td
from shiny import ui
from faicons import icon_svg


def output_code_sample(title, name_of_render_function: str):
    return table(
        tr(
            td(title).add_style(
                """
                width: 0;
                white-space: nowrap;
                padding-right: 1em;
                vertical-align: top;"""
            ),
            td(
                details(
                    summary(f"Code sample"),
                    ui.output_code(name_of_render_function),
                )
            ),
        )
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
