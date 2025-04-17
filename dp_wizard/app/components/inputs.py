from math import log10
from shiny import ui


def log_slider(id: str, lower_bound: float, upper_bound: float):
    # Rather than engineer a new widget, hide the numbers we don't want,
    # and insert the log values via CSS.
    # "display" and "visibility" were also hiding the content provided via CSS,
    # but "font-size" seems to work.
    #
    # The rendered widget doesn't have a unique ID, but the following
    # element does, so we can use some fancy CSS to get the preceding element.
    # Long term solution is just to make our own widget.
    return [
        ui.HTML(
            f"""
<style>
.irs:has(+ #{id}) .irs-single {{
    /* Hide the current, non-log value. */
    visibility: hidden;
}}
.irs:has(+ #{id}) .irs-min, .irs:has(+ #{id}) .irs-max {{
    /* Always show the endpoint values. */
    visibility: visible !important;
}}

.irs:has(+ #{id}) .irs-min, .irs:has(+ #{id}) .irs-max {{
    /* Shrink the non-log endpoint values to invisibility... */
    font-size: 0;
}}
.irs:has(+ #{id}) .irs-min::before {{
    /* ... and instead show lower ... */
    content: "{lower_bound}";
    font-size: 12px;
}}
.irs:has(+ #{id}) .irs-max::after {{
    /* ... and upper bounds. */
    content: "{upper_bound}";
    font-size: 12px;
}}
</style>
"""
        ),
        ui.input_slider(id, None, log10(lower_bound), log10(upper_bound), 0, step=0.1),
    ]
