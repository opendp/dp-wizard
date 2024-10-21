from math import log10
from shiny import ui


def log_slider(id, lower, upper):
    # Rather than engineer a new widget, hide the numbers we don't want.
    # The rendered widget doesn't have a unique ID, but the following
    # element does, so we can use some fancy CSS to get the preceding element.
    # Long term solution is just to make our own widget.
    return (
        ui.tags.table(
            ui.HTML(
                f"""
<style>
.irs:has(+ #{id}) .irs-min, .irs-max, .irs-single {{
    display: none;
}}
</style>
"""
            ),
            ui.tags.tr(
                ui.tags.td(lower),
                ui.tags.td(
                    ui.input_slider(id, None, log10(lower), log10(upper), 0, step=0.1),
                ),
                ui.tags.td(upper),
            ),
        ),
    )
