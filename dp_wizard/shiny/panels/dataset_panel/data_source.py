from dp_wizard import package_root
from dp_wizard.shiny.components.outputs import (
    hide_if,
    warning_md_box,
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
                "- Only the public data contains: "
                + ", ".join(f"`{name}`" for name in just_public)
            )
        if just_private:
            messages.append(
                "- Only the private data contains: "
                + ", ".join(f"`{name}`" for name in just_private)
            )
    return hide_if(not messages, warning_md_box("\n".join(messages)))
