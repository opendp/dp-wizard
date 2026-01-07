from shiny import reactive, ui

from dp_wizard import registry_url
from dp_wizard.shiny.components.icons import budget_icon
from dp_wizard.shiny.components.inputs import log_slider
from dp_wizard.shiny.components.outputs import code_sample, tutorial_box
from dp_wizard.utils.code_generators import make_privacy_loss_block


def privacy_budget_card_ui(
    epsilon: reactive.Value[float],
    is_tutorial_mode: reactive.Value[bool],
    max_rows: reactive.Value[str],
):
    return (
        ui.card(
            ui.card_header(budget_icon, "Privacy Budget"),
            ui.markdown(
                f"""
                What is your privacy budget for this release?
                Many factors including the sensitivity of your data,
                the frequency of DP releases,
                and the regulatory landscape can be considered.
                Consider how your budget compares to that of
                <a href="{registry_url}"
                    target="_blank">other projects</a>.
                """
            ),
            log_slider(
                "log_epsilon_slider",
                lower_bound=0.1,
                upper_bound=10.0,
                lower_message="Better Privacy",
                upper_message="Better Accuracy",
            ),
            ui.output_ui("epsilon_ui"),
            ui.output_ui("privacy_loss_python_ui"),
        ),
    )


def epsilon_ui(
    epsilon: reactive.Value[float],
    is_tutorial_mode: reactive.Value[bool],
):
    e_value = epsilon()
    extra = ""
    if e_value >= 5:
        extra = (
            ": The use of a value this **large** is discouraged "
            "because it may compromise privacy."
        )
    if e_value <= 0.2:
        extra = (
            ": The use of a value this **small** is discouraged "
            "because the additional noise will lower the accuracy of results."
        )
    return [
        ui.markdown(f"Privacy Budget (Epsilon): {e_value}{extra}"),
        tutorial_box(
            is_tutorial_mode(),
            """
            If you set epsilon above one, you'll see that the distribution
            becomes less noisy, and the confidence intervals become smaller...
            but increased accuracy risks revealing personal information.
            """,
            responsive=False,
        ),
    ]


def privacy_loss_python_ui(
    epsilon: reactive.Value[float],
    max_rows: reactive.Value[str],
):
    return code_sample(
        "Privacy Loss",
        make_privacy_loss_block(
            pure=False, epsilon=epsilon(), max_rows=int(max_rows())
        ),
    )
