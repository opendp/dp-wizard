import re
from pathlib import Path
from shutil import make_archive
from tempfile import TemporaryDirectory

from dp_wizard_templates.converters import (
    convert_nb_to_html,
    convert_py_to_nb,
)
from faicons import icon_svg
from shiny import Inputs, Outputs, Session, reactive, render, types, ui

from dp_wizard import package_root
from dp_wizard.shiny.components.outputs import (
    hide_if,
    info_md_box,
    only_for_screenreader,
    tutorial_box,
)
from dp_wizard.shiny.panels.results_panel.download_options import (
    download_button_or_link,
    download_options,
)
from dp_wizard.types import AppState
from dp_wizard.utils.code_generators import AnalysisPlan, AnalysisPlanColumn
from dp_wizard.utils.code_generators.notebook_generator import (
    PLACEHOLDER_CSV_NAME,
    NotebookGenerator,
)
from dp_wizard.utils.code_generators.script_generator import ScriptGenerator

_wait_message = "Please wait."
_target_path = package_root / ".local-sessions"


def _strip_ansi(e) -> str:
    """
    >>> e = Exception('\x1b[0;31mValueError\x1b[0m: ...')
    >>> _strip_ansi(e)
    'ValueError: ...'
    """
    # From https://stackoverflow.com/a/14693789
    import re

    return re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", str(e))


def _make_download_or_modal_error(download_generator):  # pragma: no cover
    try:
        with ui.Progress() as progress:
            progress.set(message=_wait_message)
            return download_generator()
    except Exception as e:
        message = _strip_ansi(e)
        modal = ui.modal(
            ui.pre(message),
            title="Error generating code",
            size="xl",
            easy_close=True,
        )
        ui.modal_show(modal)
        raise types.SilentException("code generation")


def results_ui():  # pragma: no cover
    return ui.nav_panel(
        "Download Results",
        ui.output_ui("results_requirements_warning_ui"),
        ui.output_ui("synthetic_data_ui"),
        ui.output_ui("download_options_ui"),
        ui.layout_columns(
            ui.output_ui("download_results_ui"),
            ui.output_ui("download_code_ui"),
        ),
        value="results_panel",
    )


def results_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    state: AppState,
):  # pragma: no cover
    # CLI options:
    # is_sample_csv = state.is_sample_csv
    in_cloud = state.in_cloud
    qa_mode = state.qa_mode

    # Top-level:
    is_tutorial_mode = state.is_tutorial_mode

    # Dataset choices:
    # initial_private_csv_path = state.initial_private_csv_path
    private_csv_path = state.private_csv_path
    # initial_public_csv_path = state.initial_private_csv_path
    public_csv_path = state.public_csv_path
    contributions = state.contributions
    contributions_entity = state.contributions_entity
    max_rows = state.max_rows
    # initial_product = state.initial_product
    product = state.product

    # Analysis choices:
    # column_names = state.column_names
    groups = state.groups
    epsilon = state.epsilon

    # Per-column choices:
    # (Note that these are all dicts, with the ColumnName as the key.)
    analysis_types = state.analysis_types
    lower_bounds = state.lower_bounds
    upper_bounds = state.upper_bounds
    bin_counts = state.bin_counts
    weights = state.weights
    # analysis_errors = state.analysis_errors

    # Release state:
    released = state.released

    @render.ui
    def results_requirements_warning_ui():
        return hide_if(
            bool(weights()),
            info_md_box(
                """
                Please define your analysis on the previous tab
                before downloading results.
                """
            ),
        )

    @reactive.calc
    def download_stem() -> str:
        return analysis_plan().to_stem()

    @reactive.calc
    def download_note() -> str:
        return analysis_plan().to_note()

    @render.ui
    def download_options_ui():
        return ui.card(
            ui.card_header("Download Options"),
            ui.markdown(
                """
                An appropriate extension for each download is added to this stem:
                """
            ),
            ui.input_text(
                "custom_download_stem",
                only_for_screenreader("Download Stem"),
                download_stem(),
            ),
            ui.markdown(
                """
                Note to include in generated notebooks and code:
                """
            ),
            ui.input_text_area(
                "custom_download_note",
                only_for_screenreader("Note to Include"),
                download_note(),
                height="6em",
                width="100%",
            ),
        )

    @reactive.calc
    def clean_download_stem() -> str:
        stem = input.custom_download_stem()
        return re.sub(r"[^A-Za-z0-9_.-]", "-", stem)[:255]

    @render.ui
    def download_results_ui():
        if in_cloud:
            return None
        disabled = not weights()
        return ui.layout_columns(
            ui.card(
                ui.card_header("Results"),
                tutorial_box(
                    is_tutorial_mode(),
                    """
                    Now you can download a notebook for your analysis.
                    The Jupyter notebook could be used locally or on Colab,
                    but the HTML version can be viewed in the brower.
                    """,
                ),
                download_button_or_link(
                    download_options["Package"],
                    primary=True,
                    disabled=disabled,
                ),
                ui.br(),
                "Contains:",
                ui.tags.ul(
                    ui.tags.li(icon_svg("file", margin_right="0.5em"), "README (.txt)"),
                    ui.tags.li(
                        download_button_or_link(
                            download_options["Notebook"],
                            primary=True,
                            disabled=disabled,
                            link=True,
                        ),
                    ),
                    ui.tags.li(
                        download_button_or_link(
                            download_options["HTML"],
                            disabled=disabled,
                            link=True,
                        ),
                    ),
                    ui.tags.li(
                        download_button_or_link(
                            download_options["Script"], disabled=disabled, link=True
                        ),
                    ),
                    ui.tags.li(
                        download_button_or_link(
                            download_options["Report"],
                            primary=True,
                            disabled=disabled,
                            link=True,
                        ),
                    ),
                    ui.tags.li(
                        download_button_or_link(
                            download_options["Table"],
                            disabled=disabled,
                            link=True,
                        ),
                    ),
                ),
            )
        )

    @render.ui
    def download_code_ui():
        disabled = not weights()
        return ui.card(
            ui.card_header("Code"),
            tutorial_box(
                is_tutorial_mode(),
                (
                    """
                    When [installed and run
                    locally](https://pypi.org/project/dp_wizard/),
                    there are more download options because DP Wizard
                    can read your private CSV and release differentially
                    private statistics.

                    In the cloud, DP Wizard only provides unexecuted
                    notebooks and scripts.
                    """
                    if in_cloud
                    else """
                    Alternatively, you can download a script or unexecuted
                    notebook that demonstrates the steps of your analysis,
                    but does not contain any data or analysis results.
                    """
                ),
            ),
            download_button_or_link(
                download_options["Notebook (unexecuted)"],
                cloud=in_cloud,
                disabled=disabled,
            ),
            download_button_or_link(
                download_options["HTML (unexecuted)"],
                disabled=disabled,
            ),
            download_button_or_link(
                download_options["Script"],
                disabled=disabled,
            ),
            download_button_or_link(
                download_options["Notebook Source"],
                disabled=disabled,
            ),
        )

    @reactive.calc
    def analysis_plan() -> AnalysisPlan:
        # weights().keys() will reflect the desired columns:
        # The others retain inactive columns, so user
        # inputs aren't lost when toggling checkboxes.
        columns = {
            col: [
                AnalysisPlanColumn(
                    analysis_name=analysis_types()[col],
                    lower_bound=lower_bounds()[col],
                    upper_bound=upper_bounds()[col],
                    bin_count=int(bin_counts()[col]),
                    weight=int(weights()[col]),
                )
            ]
            for col in weights().keys()
        }
        return AnalysisPlan(
            product=product(),
            # Prefer private CSV, if available:
            csv_path=private_csv_path() or public_csv_path() or PLACEHOLDER_CSV_NAME,
            contributions=contributions(),
            contributions_entity=contributions_entity(),
            epsilon=epsilon(),
            max_rows=int(max_rows()),
            groups=groups(),
            columns=columns,
        )

    ################################
    #
    # Generate content for downloads
    #
    ################################

    @reactive.calc
    def table_of_contents_md():
        included_names = ["Notebook", "HTML", "Script", "Report", "Table"]
        included_options = [download_options[name] for name in included_names]
        return "- README.txt\n" + "\n".join(
            f"- {opt.name} ({opt.ext}): {opt.clean_description_md}"
            for opt in included_options
        )

    @reactive.calc
    def package_zip():
        with TemporaryDirectory() as tmp_dir:
            zip_root_dir = Path(tmp_dir) / "zip-root"
            zip_root_dir.mkdir()

            stem = input.custom_download_stem()
            note = input.custom_download_note()

            toc = table_of_contents_md()
            readme = f"# {analysis_plan()}\n\n{note}\n\nContains:\n\n{toc}"

            (zip_root_dir / "README.txt").write_text(readme)
            (zip_root_dir / f"{stem}.ipynb").write_text(notebook_nb())
            (zip_root_dir / f"{stem}.html").write_text(notebook_html())
            (zip_root_dir / f"{stem}.py").write_text(script_py())
            # This is a little bit redundant, since these have already
            # been written out as files, but it's safer to start
            # from a clean slate, rather than rely on the side effect
            # of a reactive.calc.
            (zip_root_dir / f"{stem}.txt").write_text(report())
            (zip_root_dir / f"{stem}.csv").write_text(table())

            base_name = f"{tmp_dir}/{stem}"
            ext = "zip"
            make_archive(
                base_name=base_name,
                format=ext,
                root_dir=zip_root_dir,
            )
            return Path(f"{base_name}.{ext}").read_bytes()

    @reactive.calc
    def notebook_py():
        if qa_mode:
            return "raise Exception('qa_mode!')"
        return NotebookGenerator(
            analysis_plan(),
            input.custom_download_note(),
        ).make_py()

    @reactive.calc
    def script_py():
        return ScriptGenerator(
            analysis_plan(),
            input.custom_download_note(),
        ).make_py()

    @reactive.calc
    def notebook_nb():
        # This creates the notebook, and evaluates it,
        # and drops reports in the local-sessions dir.
        # Could be slow!
        # Luckily, reactive calcs are lazy.

        # TODO: reactive.calcs shouldn't have side-effects!
        # (Like writing files that other calcs will depend on.)
        # https://github.com/opendp/dp-wizard/issues/682
        released.set(True)
        plan = analysis_plan()
        return convert_py_to_nb(notebook_py(), title=str(plan), execute=True)

    @reactive.calc
    def notebook_nb_unexecuted():
        plan = analysis_plan()
        return convert_py_to_nb(notebook_py(), title=str(plan), execute=False)

    @reactive.calc
    def notebook_html():
        return convert_nb_to_html(notebook_nb())

    @reactive.calc
    def notebook_html_unexecuted():
        return convert_nb_to_html(notebook_nb_unexecuted())

    @reactive.calc
    def report():
        notebook_nb()  # Evaluate just for the side effect of creating report.
        return (_target_path / "report.txt").read_text()

    @reactive.calc
    def table():
        notebook_nb()  # Evaluate just for the side effect of creating report.
        return (_target_path / "report.csv").read_text()

    ######################
    #
    # Handle the downloads
    #
    ######################

    # Function names need to match the id constructed by button(),
    # based on the cleaned-up name parameter.

    def download(ext: str):
        """
        Rather than dealing with @render.download() directly,
        this decorator derives MIME type from the
        provided extension.
        """
        last_ext = ext.split(".")[-1]
        mime = {
            "zip": "application/zip",
            "ipynb": "application/x-ipynb+json",
            "py": "text/x-python",
            "html": "text/html",
            "csv": "text/csv",
            "txt": "text/plain",
        }.get(last_ext)
        if mime is None:
            raise Exception(f"No MIME type for {ext}")

        def inner(func):
            wrapped = render.download(
                filename=lambda: clean_download_stem() + ext,
                media_type=mime,
            )(func)
            return wrapped

        return inner

    @download(".zip")
    async def download_package_button():
        yield _make_download_or_modal_error(package_zip)

    @download(".py")
    async def download_script_link():
        yield _make_download_or_modal_error(script_py)

    @download(".py")
    async def download_script_button():
        yield _make_download_or_modal_error(script_py)

    @download(".ipynb.py")
    async def download_notebook_source_button():
        yield _make_download_or_modal_error(notebook_py)

    @download(".ipynb")
    async def download_notebook_link():
        yield _make_download_or_modal_error(notebook_nb)

    @download(".unexecuted.ipynb")
    async def download_notebook_unexecuted_button():
        yield _make_download_or_modal_error(notebook_nb_unexecuted)

    @download(".html")
    async def download_html_link():
        yield _make_download_or_modal_error(notebook_html)

    @download(".unexecuted.html")
    async def download_html_unexecuted_button():
        yield _make_download_or_modal_error(notebook_html_unexecuted)

    @download(".txt")
    async def download_report_link():
        yield _make_download_or_modal_error(report)

    @download(".csv")
    async def download_table_link():
        yield _make_download_or_modal_error(table)
