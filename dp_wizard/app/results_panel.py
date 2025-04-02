from pathlib import Path
import re

from shiny import ui, render, reactive, Inputs, Outputs, Session, types
from faicons import icon_svg
from htmltools.tags import p

from dp_wizard.utils.code_generators import (
    AnalysisPlan,
    AnalysisPlanColumn,
)
from dp_wizard.utils.code_generators.notebook_generator import NotebookGenerator
from dp_wizard.utils.code_generators.script_generator import ScriptGenerator
from dp_wizard.utils.converters import (
    convert_py_to_nb,
    convert_nb_to_html,
    convert_nb_to_pdf,
)


wait_message = "Please wait."


def button(name: str, ext: str, icon: str, primary=False):
    clean_name = re.sub(r"\W+", " ", name).strip().replace(" ", "_").lower()
    function_name = f"download_{clean_name}"
    return ui.download_button(
        function_name,
        f"Download {name} ({ext})",
        icon=icon_svg(icon, margin_right="0.5em"),
        width="20em",
        class_="btn-primary" if primary else None,
    )


def results_ui():
    return ui.nav_panel(
        "Download Results",
        ui.h3("Download Results"),
        ui.p("You can now make a differentially private release of your data."),
        # Find more icons on Font Awesome: https://fontawesome.com/search?ic=free
        ui.accordion(
            ui.accordion_panel(
                "Notebooks",
                button("Notebook", ".ipynb", "book", primary=True),
                p(
                    """
                    An executed Jupyter notebook which references your CSV
                    and shows the result of a differentially private analysis.
                    """
                ),
                button("HTML", ".html", "file-code"),
                p("The same content, but exported as HTML."),
                button("PDF", ".pdf", "file-pdf"),
                p("The same content, but exported as PDF."),
            ),
            ui.accordion_panel(
                "Reports",
                button("Report", ".txt", "file-lines", primary=True),
                p(
                    """
                    A report which includes your parameter choices and the results.
                    Intended to be human-readable, but it does use YAML,
                    so it can be parsed by other programs.
                    """
                ),
                button("Table", ".csv", "file-csv"),
                p("The same information, but condensed into a two-column CSV."),
            ),
        ),
        ui.h3("Download code"),
        ui.p(
            """
            Alternatively, you can download a script or unexecuted notebook
            that demonstrates the steps of your analysis,
            but does not contain any data or analysis results.
            """
        ),
        ui.accordion(
            ui.accordion_panel(
                "Unexecuted Notebooks",
                button("Notebook (unexecuted)", ".ipynb", "book", primary=True),
                p(
                    """
                    This contains the same code as Jupyter notebook above,
                    but none of the cells are executed,
                    so it does not contain any results.
                    """
                ),
                button("HTML (unexecuted)", ".html", "file-code"),
                p("The same content, but exported as HTML."),
                button("PDF (unexecuted)", ".pdf", "file-pdf"),
                p("The same content, but exported as PDF."),
            ),
            ui.accordion_panel(
                "Scripts",
                button("Script", ".py", "python", primary=True),
                p(
                    """
                    The same code as the notebooks, but extracted into
                    a Python script which can be run from the command line.
                    """
                ),
                button("Notebook Source", ".py", "python"),
                p(
                    """
                    Python source code converted by jupytext into notebook.
                    Primarily of interest to DP Wizard developers.
                    """
                ),
            ),
            open=False,
        ),
        value="results_panel",
    )


def make_download_or_modal_error(download_generator) -> str:  # pragma: no cover
    try:
        with ui.Progress() as progress:
            progress.set(message=wait_message)
            return download_generator()
    except Exception as e:
        modal = ui.modal(
            ui.pre(str(e)),
            title="Error generating code",
            size="xl",
        )
        ui.modal_show(modal)
        raise types.SilentException("code generation")


def results_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    public_csv_path: reactive.Value[str],
    private_csv_path: reactive.Value[str],
    contributions: reactive.Value[int],
    analysis_types: reactive.Value[dict[str, str]],
    lower_bounds: reactive.Value[dict[str, float]],
    upper_bounds: reactive.Value[dict[str, float]],
    bin_counts: reactive.Value[dict[str, int]],
    groups: reactive.Value[list[str]],
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
                analysis_type=analysis_types()[col],
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
            groups=groups(),
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

    @reactive.calc
    def notebook_nb_unexecuted():
        notebook_py = NotebookGenerator(analysis_plan()).make_py()
        return convert_py_to_nb(notebook_py, execute=False)

    @reactive.calc
    def notebook_html():
        return convert_nb_to_html(notebook_nb())

    @reactive.calc
    def notebook_html_unexecuted():
        return convert_nb_to_html(notebook_nb_unexecuted())

    @reactive.calc
    def notebook_pdf():
        return convert_nb_to_pdf(notebook_nb())

    @reactive.calc
    def notebook_pdf_unexecuted():
        return convert_nb_to_pdf(notebook_nb_unexecuted())

    @render.download(
        filename="dp-wizard-script.py",
        media_type="text/x-python",
    )
    async def download_script():
        yield make_download_or_modal_error(ScriptGenerator(analysis_plan()).make_py)

    @render.download(
        filename="dp-wizard-notebook.py",
        media_type="text/x-python",
    )
    async def download_notebook_source():
        with ui.Progress() as progress:
            progress.set(message=wait_message)
            yield NotebookGenerator(analysis_plan()).make_py()

    @render.download(
        filename="dp-wizard-notebook.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook():
        yield make_download_or_modal_error(notebook_nb)

    @render.download(
        filename="dp-wizard-notebook-unexecuted.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook_unexecuted():
        yield make_download_or_modal_error(notebook_nb_unexecuted)

    @render.download(  # pyright: ignore
        filename="dp-wizard-notebook.html",
        media_type="text/html",
    )
    async def download_html():
        yield make_download_or_modal_error(notebook_html)

    @render.download(  # pyright: ignore
        filename="dp-wizard-notebook-unexecuted.html",
        media_type="text/html",
    )
    async def download_html_unexecuted():
        yield make_download_or_modal_error(notebook_html_unexecuted)

    @render.download(
        filename="dp-wizard-notebook.pdf",
        media_type="application/pdf",
    )  # pyright: ignore
    async def download_pdf():
        yield make_download_or_modal_error(notebook_pdf)

    @render.download(
        filename="dp-wizard-notebook.pdf",
        media_type="application/pdf",
    )  # pyright: ignore
    async def download_pdf_unexecuted():
        yield make_download_or_modal_error(notebook_pdf_unexecuted)

    @render.download(
        filename="dp-wizard-report.txt",
        media_type="text/plain",
    )
    async def download_report():
        def make_report():
            notebook_nb()  # Evaluate just for the side effect of creating report.
            return (Path(__file__).parent.parent / "tmp" / "report.txt").read_text()

        yield make_download_or_modal_error(make_report)

    @render.download(
        filename="dp-wizard-report.csv",
        media_type="text/plain",
    )
    async def download_table():
        def make_table():
            notebook_nb()  # Evaluate just for the side effect of creating report.
            return (Path(__file__).parent.parent / "tmp" / "report.csv").read_text()

        yield make_download_or_modal_error(make_table)
