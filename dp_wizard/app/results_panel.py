from pathlib import Path

from shiny import ui, render, reactive, Inputs, Outputs, Session
from faicons import icon_svg
from htmltools.tags import table, tr, td

from dp_wizard.utils.code_generators import (
    NotebookGenerator,
    ScriptGenerator,
    AnalysisPlan,
    AnalysisPlanColumn,
)
from dp_wizard.utils.converters import convert_py_to_nb, strip_nb_coda


wait_message = "Please wait."


def td_button(name: str, ext: str, icon: str):
    function_name = f'download_{name.lower().replace(" ", "_")}'
    return (
        td(
            ui.download_button(
                function_name,
                [
                    icon_svg(icon, margin_right="0.5em"),
                    f"Download {name} ({ext})",
                ],
                width="20em",
            )
        ),
    )


def results_ui():
    return ui.nav_panel(
        "Download results",
        ui.markdown("You can now make a differentially private release of your data."),
        table(
            tr(
                td_button("Notebook", ".ipynb", "book"),
                td_button("Script", ".py", "python"),
            ),
            tr(
                td_button("Report", ".txt", "file-lines"),
                td_button("Table", ".csv", "file-csv"),
            ),
        ),
        value="results_panel",
    )


def results_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    public_csv_path: reactive.Value[str],
    private_csv_path: reactive.Value[str],
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
            # Prefer private CSV, if available:
            csv_path=private_csv_path() or public_csv_path(),
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
        notebook_json = convert_py_to_nb(notebook_py, execute=True)
        return strip_nb_coda(notebook_json)

    @render.download(
        filename="dp-wizard-script.py",
        media_type="text/x-python",
    )
    async def download_script():
        with ui.Progress() as progress:
            progress.set(message=wait_message)
            yield ScriptGenerator(analysis_plan()).make_py()

    @render.download(
        filename="dp-wizard-notebook.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook():
        with ui.Progress() as progress:
            progress.set(message=wait_message)
            yield notebook_nb()

    @render.download(
        filename="dp-wizard-report.txt",
        media_type="text/plain",
    )
    async def download_report():
        with ui.Progress() as progress:
            progress.set(message=wait_message)
            notebook_nb()  # Evaluate just for the side effect of creating report.
            report_txt = (
                Path(__file__).parent.parent / "tmp" / "report.txt"
            ).read_text()
            yield report_txt

    @render.download(
        filename="dp-wizard-report.csv",
        media_type="text/plain",
    )
    async def download_table():
        with ui.Progress() as progress:
            progress.set(message=wait_message)
            notebook_nb()  # Evaluate just for the side effect of creating report.
            report_csv = (
                Path(__file__).parent.parent / "tmp" / "report.csv"
            ).read_text()
            yield report_csv
