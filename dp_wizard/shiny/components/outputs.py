import re

from faicons import icon_svg
from htmltools.tags import code, details, pre, script, small, summary
from shiny import ui

col_widths = {
    # Controls stay roughly a constant width;
    # Graph expands to fill space.
    "sm": [4, 8],
    "md": [3, 9],
    "lg": [2, 10],
}


def output_code_sample(title, name_of_render_function: str):
    # Syntax highlighting proposed as a feature for shiny:
    # https://github.com/posit-dev/py-shiny/issues/491
    # If there is progress there, this could be simplified,
    # and we could removed the vendored highlight.js.

    #     text = ui.output_text(name_of_render_function)
    #     print(text)
    #     return details(
    #         summary(["Code sample: ", title]),
    #         ui.markdown(
    #                 f"""```python
    # {text}
    # ```
    # """),
    #         script("hljs.highlightAll();") # This could be narrowed to just the current element.
    #     )

    # Doesn't work: div is marked as `data-highlighted="yes"`
    # but there are no colors: maybe the classes conflict,
    # Or shiny re-writes the content again?
    #
    def container(*args, **kwargs):
        kwargs["class_"] += " language-python"
        return (pre(code(*args, **kwargs)),)

    content = ui.output_text(name_of_render_function, container=container)
    breakpoint()
    print(content.render())
    return details(
        summary(["Code sample: ", title]),
        content,
        script("hljs.highlightAll();"),  # This could be narrowed.
    )

    # This works:
    #
    # return ui.HTML("""
    # <pre><code class="language-python">
    #     def fake(param):
    #         print(f"hello? {param}")
    # </code></pre>
    # <script>hljs.highlightAll();</script>
    # """)


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
