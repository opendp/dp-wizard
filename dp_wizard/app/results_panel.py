from pathlib import Path

from shiny import ui, render, reactive, Inputs, Outputs, Session

from dp_wizard.utils.code_generators import (
    NotebookGenerator,
    ScriptGenerator,
    AnalysisPlan,
    AnalysisPlanColumn,
)
from dp_wizard.utils.converters import convert_py_to_nb


def results_ui():
    return ui.nav_panel(
        "Download results",
        ui.markdown("You can now make a differentially private release of your data."),
        ui.download_button(
            "download_report",
            "Download Report (.txt)",
        ),
        ui.download_button(
            "download_script",
            "Download Script (.py)",
        ),
        ui.download_button(
            "download_notebook",
            "Download Notebook (.ipynb)",
        ),
        value="results_panel",
    )


def results_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    csv_path: reactive.Value[str],
    contributions: reactive.Value[int],
    lower_bounds: reactive.Value[dict[str, float]],
    upper_bounds: reactive.Value[dict[str, float]],
    bin_counts: reactive.Value[dict[str, int]],
    weights: reactive.Value[dict[str, str]],
    epsilon: reactive.Value[float],
):  # pragma: no cover
    @reactive.calc
    def analysis_plan() -> AnalysisPlan:
        # weights().keys() will reflect the desired columns:
        # The others retain inactive columns, so user
        # inputs aren't lost when toggling checkboxes.
        columns = {
            col: AnalysisPlanColumn(
                lower_bound=lower_bounds()[col],
                upper_bound=upper_bounds()[col],
                bin_count=int(bin_counts()[col]),
                weight=int(weights()[col]),
            )
            for col in weights().keys()
        }
        return AnalysisPlan(
            csv_path=csv_path(),
            contributions=contributions(),
            epsilon=epsilon(),
            columns=columns,
        )

    @reactive.calc
    def notebook_nb():
        # This creates the notebook, and evaluates it,
        # and drops reports in the tmp dir.
        # Could be slow!
        # Luckily, reactive calcs are lazy.
        notebook_py = NotebookGenerator(analysis_plan()).make_py()
        return convert_py_to_nb(notebook_py, execute=True)

    @render.download(
        filename="dp-wizard-script.py",
        media_type="text/x-python",
    )
    async def download_script():
        script_py = ScriptGenerator(analysis_plan()).make_py()
        yield script_py

    @render.download(
        filename="dp-wizard-notebook.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook():
        yield notebook_nb()

    @render.download(
        filename="dp-wizard-report.txt",
        media_type="text/plain",
    )
    async def download_report():
        notebook_nb()  # Evaluate just for the side effect of creating report.
        report_txt = (Path(__file__).parent.parent / "tmp" / "report.txt").read_text()
        yield report_txt
