from shiny import ui
from htmltools import HTML


def feedback_ui():
    return ui.nav_panel(
        "Feedback",
        ui.div(
            HTML(
                """
                <iframe
                    src="https://docs.google.com/forms/d/e/1FAIpQLScaGdKS-vj-RrM7SCV_lAwZmxQ2bOqFrAkyDp4djxTqkTkinA/viewform?embedded=true"
                    id="feedback-iframe"
                    width="640"
                    height="1003"
                    frameborder="0"
                    marginheight="0"
                    marginwidth="0"
                >Loading…</iframe>
                """
            )
        ),
        value="feedback_panel",
    )


def feedback_server(
    input,
    output,
    session,
):  # pragma: no cover
    pass
