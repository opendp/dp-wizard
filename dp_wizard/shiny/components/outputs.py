import re

from faicons import icon_svg
from htmltools.tags import details, small, summary
from shiny import ui

col_widths = {
    # Controls stay roughly a constant width;
    # Graph expands to fill space.
    "sm": [4, 8],
    "md": [3, 9],
    "lg": [2, 10],
}


def output_code_sample(title, name_of_render_function: str):
    return details(
        summary(["Code sample: ", title]),
        ui.output_code(name_of_render_function),
    )


def tutorial_box(
    is_tutorial: bool,
    markdown: str,
    show_extra: bool = False,
    extra_markdown: str = "",
    responsive: bool = True,
):
    """
    >>> assert None == tutorial_box(False, '**Testing** 123')

    >>> html = str(tutorial_box(True, '**Testing** 123'))
    >>> assert '<p><svg' in html
    >>> assert '</svg>&nbsp;<strong>Testing' in html

    """
    if is_tutorial:
        responsive_classes = "col-md-8 col-lg-6 col-xl-4" if responsive else ""
        inner_html = small(
            icon_svg("circle-question"),
            ui.markdown(f"{markdown}\n\n{extra_markdown if show_extra else ''}"),
        )
        # Move the SVG icon inside the first element:
        inner_html = re.sub(r"(<svg.+?</svg>)(<.+?>)", r"\2\1&nbsp;", str(inner_html))
        return ui.div(
            small(ui.HTML(inner_html)),
            class_=f"alert alert-info p-2 {responsive_classes}",
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
