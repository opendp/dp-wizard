from dp_wizard import package_root
from dp_wizard.shiny.components.outputs import (
    code_sample,
    hide_if,
    warning_md_box,
)
from dp_wizard.utils.code_generators import DefaultsTemplate


def context_code_sample():
    return code_sample(
        "Context",
        DefaultsTemplate(
            # NOTE: If stats vs. synth is moved to the top of the flow,
            # then we can show the appropriate template here.
            "stats_context",
            package_root / "utils/code_generators/no-tests",
        )
        .fill_values(CSV_PATH="demo.csv")
        .fill_expressions(
            MARGINS_LIST="margins",
            EXTRA_COLUMNS="extra_columns",
            WEIGHTS="weights",
        )
        .fill_blocks(
            PRIVACY_UNIT_BLOCK="",
            PRIVACY_LOSS_BLOCK="",
            OPTIONAL_CSV_BLOCK=(
                "# More of these slots will be filled in\n"
                "# as you move through DP Wizard.\n"
            ),
        )
        .finish()
        .strip(),
    )


def csv_message_ui(
    csv_column_mismatch_calc,
    csv_messages: list[str],
):  # pragma: no cover
    messages = [f"- {m}" for m in csv_messages]
    mismatch = csv_column_mismatch_calc()
    if mismatch:
        just_public, just_private = mismatch
        if just_public:
            messages.append(
                "- Only the public CSV contains: "
                + ", ".join(f"`{name}`" for name in just_public)
            )
        if just_private:
            messages.append(
                "- Only the private CSV contains: "
                + ", ".join(f"`{name}`" for name in just_private)
            )
    return hide_if(not messages, warning_md_box("\n".join(messages)))
