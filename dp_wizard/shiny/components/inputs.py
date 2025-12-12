from math import log10

from shiny import ui

from dp_wizard.shiny.components.outputs import only_for_screenreader


def log_slider(
    id: str,
    lower_bound: float,
    upper_bound: float,
    lower_message: str = "",
    upper_message: str = "",
):
    # Rather than engineer a new widget, hide the numbers we don't want,
    # and insert the log values via CSS.
    # "display" and "visibility" were also hiding the content provided via CSS,
    # but "font-size" seems to work.
    #
    # The rendered widget doesn't have a unique ID, but the following
    # element does, so we can use some fancy CSS to get the preceding element.
    # Long term solution is just to make our own widget.
    target = f".irs:has(+ #{id})"
    lower_content = lower_message if lower_message else lower_bound
    upper_content = upper_message if upper_message else upper_bound
    return [
        ui.HTML(
            f"""
<style>
{target} .irs-bar {{
    /* Line from left is visual clutter, but useful for tests. */
    opacity: 0;
}}
{target} .irs-line {{
    /* Warn about high or low values. */
    top: 29px;
    height: 7px;
    background: linear-gradient(to right, red, lightgrey, lightgrey, red);
    border: 0.9px solid #8D959E; /* To match bootstrap. */
}}
{target} .irs-handle {{
    /* Match .irs-line: */
    border: 2px solid #8D959E; /* To match bootstrap. */
    background-color: white;
}}

{target} .irs-single {{
    /* Hide the current, non-log value. */
    visibility: hidden;
}}

{target} .irs-min, {target} .irs-max {{
    /* Shrink the non-log endpoint values to invisibility... */
    font-size: 0;
    /* and instead show messages... */
    visibility: visible !important;
}}
{target} .irs-min::before {{
    /* ... using css "content": */
    content: "{lower_content}";
    font-size: 12px;
}}
{target} .irs-max::after {{
    content: "{upper_content}";
    font-size: 12px;
}}
</style>
"""
        ),
        ui.input_slider(
            id,
            only_for_screenreader("Epsilon"),
            log10(lower_bound),
            log10(upper_bound),
            0,
            step=0.1,
        ),
    ]
