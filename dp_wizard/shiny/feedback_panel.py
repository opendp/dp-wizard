from shiny import ui, Inputs, Outputs, Session
from htmltools import HTML


def feedback_ui():
    return ui.nav_panel(
        "Feedback",
        ui.div(
            HTML(
                # Responses to this survey are at:
                # https://docs.google.com/forms/d/1l7-RK1R1nRuhHr8pTck1D4RU8Bi6Ehr124bkYvH-96c/edit
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
    input: Inputs,
    output: Outputs,
    session: Session,
):  # pragma: no cover
    pass
