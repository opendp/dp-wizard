import re

from faicons import icon_svg
from htmltools.tags import details, script, small, summary
from shiny import ui

col_widths = {
    # Controls stay roughly a constant width;
    # Graph expands to fill space.
    "sm": [4, 8],
    "md": [3, 9],
    "lg": [2, 10],
}


def code_sample(title: str, python_block: str):
    """
    >>> code_sample('test', 'print("hello, world")')
    <details>
      <summary>
        Code sample: test
      </summary>
      <pre><code class="language-python">print(&quot;hello, world&quot;)
    </code></pre>
    <BLANKLINE>
      <script>hljs.highlightAll();</script>
    </details>
    """
    # Based on: https://github.com/posit-dev/py-shiny/issues/491
    # If that is incorporated into Shiny, this could be simplified.
    return details(
        summary(["Code sample: ", title]),
        ui.markdown(f"```python\n{python_block}\n```"),
        script(
            "hljs.highlightAll();"
        ),  # This could be narrowed to just the current element.
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

    >>> empty_column = 'html-fill-container"></div>'
    >>> assert empty_column in html

    >>> non_responsive = str(tutorial_box(True, '**Testing** 123', responsive=False))
    >>> assert empty_column not in non_responsive

    """
    if is_tutorial:
        inner_html = small(
            icon_svg("circle-question"),
            ui.markdown(f"{markdown}\n\n{extra_markdown if show_extra else ''}"),
        )
        # Move the SVG icon inside the first element:
        inner_html = re.sub(r"(<svg.+?</svg>)(<.+?>)", r"\2\1&nbsp;", str(inner_html))
        columns: list = [
            ui.div(
                ui.HTML(inner_html),
                class_="alert alert-info p-2",
            )
        ]
        if responsive:
            # Bootstrap classes ("col-lg-6") don't give us padding for the gutter.
            # Using columns here makes sure we line up with panels below.
            columns.append(None)
        return ui.layout_columns(*columns)


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
