from math import log10

from shiny import ui

from dp_wizard.shiny.components.outputs import only_for_screenreader


def log_slider(id: str, lower_bound: float, upper_bound: float):
    # Rather than engineer a new widget, hide the numbers we don't want,
    # and insert the log values via CSS.
    # "display" and "visibility" were also hiding the content provided via CSS,
    # but "font-size" seems to work.
    #
    # The rendered widget doesn't have a unique ID, but the following
    # element does, so we can use some fancy CSS to get the preceding element.
    # Long term solution is just to make our own widget.
    target = f".irs:has(+ #{id})"
    return [
        ui.HTML(
            f"""
<style>
{target} .irs-line {{
    top: 29px;
    height: 7px;
    background: linear-gradient(to right, blue, white, white, red);
}}
{target} .irs-bar {{
    display: none;
}}
{target} .irs-single {{
    /* Hide the current, non-log value. */
    visibility: hidden;
}}
{target} .irs-min, {target} .irs-max {{
    /* Always show the endpoint values. */
    visibility: visible !important;
    /* Shrink the non-log endpoint values to invisibility... */
    font-size: 0;
}}
{target} .irs-min::before {{
    /* ... and instead show lower ... */
    content: "{lower_bound}";
    font-size: 12px;
}}
{target} .irs-max::after {{
    /* ... and upper bounds. */
    content: "{upper_bound}";
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
