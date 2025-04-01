from pathlib import Path
from typing import Optional

from shiny import ui, reactive, render, Inputs, Outputs, Session

from dp_wizard.utils.argparse_helpers import (
    PUBLIC_TEXT,
    PRIVATE_TEXT,
    PUBLIC_PRIVATE_TEXT,
    CLIInfo,
)
from dp_wizard.utils.csv_helper import get_csv_names_mismatch
from dp_wizard.app.components.outputs import (
    output_code_sample,
    demo_tooltip,
    hide_if,
    info_md_box,
)
from dp_wizard.utils.code_generators import make_privacy_unit_block


dataset_panel_id = "dataset_panel"


def dataset_ui():
    return ui.nav_panel(
        "Select Dataset",
        ui.card(
            ui.card_header("Input CSVs"),
            ui.markdown(
                f"""
Choose **Public CSV** {PUBLIC_TEXT}

Choose **Private CSV** {PRIVATE_TEXT}

Choose both **Public CSV** and **Private CSV** {PUBLIC_PRIVATE_TEXT}"""
            ),
            ui.output_ui("input_files_ui"),
            ui.output_ui("csv_column_match_ui"),
        ),
        ui.card(
            ui.card_header("Unit of privacy"),
            ui.markdown(
                "How many rows of the CSV can one individual contribute to? "
                'This is the "unit of privacy" which will be protected.'
            ),
            ui.output_ui("input_contributions_ui"),
            ui.output_ui("contributions_validation_ui"),
            output_code_sample(
                ["Unit of Privacy", ui.output_ui("python_tooltip_ui")],
                "unit_of_privacy_python",
            ),
        ),
        ui.output_ui("define_analysis_button_ui"),
        value="dataset_panel",
    )


def dataset_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    cli_info: CLIInfo,
    public_csv_path: reactive.Value[str],
    private_csv_path: reactive.Value[str],
    contributions: reactive.Value[int],
):  # pragma: no cover
    @reactive.effect
    @reactive.event(input.public_csv_path)
    def _on_public_csv_path_change():
        public_csv_path.set(input.public_csv_path()[0]["datapath"])

    @reactive.effect
    @reactive.event(input.private_csv_path)
    def _on_private_csv_path_change():
        private_csv_path.set(input.private_csv_path()[0]["datapath"])

    @reactive.calc
    def csv_column_mismatch_calc() -> Optional[tuple[set, set]]:
        public = public_csv_path()
        private = private_csv_path()
        if public and private:
            just_public, just_private = get_csv_names_mismatch(
                Path(public), Path(private)
            )
            if just_public or just_private:
                return just_public, just_private

    @render.ui
    def input_files_ui():
        # We can't set the actual value of a file input,
        # but the placeholder string is a good substitute.
        #
        # Make sure this doesn't depend on reactive values,
        # for two reasons:
        # - If there is a dependency, the inputs are redrawn,
        #   and it looks like the file input is unset.
        # - After file upload, the internal copy of the file
        #   is renamed to something like "0.csv".
        return ui.row(
            ui.input_file(
                "public_csv_path",
                [
                    "Choose Public CSV ",  # Trailing space looks better.
                    demo_tooltip(
                        cli_info.is_demo,
                        "For the demo, we'll imagine we have the grades "
                        "on assignments for a class.",
                    ),
                ],
                accept=[".csv"],
                placeholder=Path(cli_info.public_csv_path or "").name,
            ),
            ui.input_file(
                "private_csv_path",
                "Choose Private CSV",
                accept=[".csv"],
                placeholder=Path(cli_info.private_csv_path or "").name,
            ),
        )

    @render.ui
    def csv_column_match_ui():
        mismatch = csv_column_mismatch_calc()
        messages = []
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
        return hide_if(not messages, info_md_box("\n".join(messages)))

    @render.ui
    def input_contributions_ui():
        return ui.row(
            ui.input_numeric(
                "contributions",
                [
                    "Contributions ",  # Trailing space looks better.
                    demo_tooltip(
                        cli_info.is_demo,
                        "For the demo, we assume that each student "
                        f"can occur at most {contributions()} times in the dataset. ",
                    ),
                ],
                contributions(),
                min=1,
            )
        )

    @reactive.effect
    @reactive.event(input.contributions)
    def _on_contributions_change():
        contributions.set(input.contributions())

    @reactive.calc
    def button_enabled():
        public_csv_path_is_set = (
            input.public_csv_path() is not None and len(input.public_csv_path()) > 0
        )
        private_csv_path_is_set = (
            input.private_csv_path() is not None and len(input.private_csv_path()) > 0
        )
        csv_path_is_set = (
            public_csv_path_is_set or private_csv_path_is_set or cli_info.is_demo
        ) and not csv_column_mismatch_calc()
        contributions_is_set = input.contributions() is not None
        return contributions_is_set and csv_path_is_set

    @reactive.calc
    def contributions_valid():
        contributions = input.contributions()
        return isinstance(contributions, int) and contributions >= 1

    @render.ui
    def contributions_validation_ui():
        return hide_if(
            contributions_valid(),
            info_md_box("Contributions must be 1 or greater."),
        )

    @render.ui
    def python_tooltip_ui():
        return demo_tooltip(
            cli_info.is_demo,
            "Along the way, code samples will demonstrate "
            "how the information you provide is used in OpenDP, "
            "and at the end you can download a notebook "
            "for the entire calculation.",
        )

    @render.ui
    def define_analysis_button_ui():
        button = ui.input_action_button(
            "go_to_analysis", "Define analysis", disabled=not button_enabled()
        )
        if button_enabled() and contributions_valid():
            return button
        return [
            button,
            "Choose CSV and Contributions before proceeding.",
        ]

    @render.code
    def unit_of_privacy_python():
        return make_privacy_unit_block(contributions())

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")
