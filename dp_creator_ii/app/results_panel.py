from json import dumps

from shiny import ui, render, reactive

from dp_creator_ii.utils.templates import make_notebook_py, make_script_py
from dp_creator_ii.utils.converters import convert_py_to_nb
from dp_creator_ii.app.components.outputs import output_code_sample


def results_ui():
    return ui.nav_panel(
        "Download results",
        ui.p("These code snippets describe how to make a DP release of your data:"),
        output_code_sample("Analysis JSON", "analysis_json_text"),  # TODO: Drop this?
        output_code_sample("Analysis Python", "analysis_python_text"),
        ui.markdown(
            "You can now make a differentially private release of your data. "
            "This will lock the configuration you’ve provided on the previous pages."
        ),
        ui.markdown(
            "You can also download code that can be executed to produce a DP release. "
            "Downloaded code does not lock the configuration."
        ),
        ui.download_button(
            "download_script",
            "Download Script (.py)",
        ),
        ui.download_button(
            "download_notebook_unexecuted",
            "Download Notebook (.ipynb)",
        ),
        value="results_panel",
    )


def results_server(
    input,
    output,
    session,
    csv_path,
    contributions,
    lower_bounds,
    upper_bounds,
    bin_counts,
    weights,
    epsilon,
):  # pragma: no cover
    @reactive.calc
    def analysis_dict():
        # weights().keys() will reflect the desired columns:
        # The others retain inactive columns, so user
        # inputs aren't lost when toggling checkboxes.
        columns = {
            col: {
                "lower_bound": lower_bounds()[col],
                "upper_bound": upper_bounds()[col],
                "bin_count": int(bin_counts()[col]),
                # TODO: Floats should work for weight, but they don't:
                # https://github.com/opendp/opendp/issues/2140
                "weight": int(weights()[col]),
            }
            for col in weights().keys()
        }
        return {
            "csv_path": csv_path(),
            "contributions": contributions(),
            "epsilon": epsilon(),
            "columns": columns,
        }

    @reactive.calc
    def analysis_json():
        return dumps(
            analysis_dict(),
            indent=2,
        )

    @render.text
    def analysis_json_text():
        return analysis_json()

    @reactive.calc
    def analysis_python():
        analysis = analysis_dict()
        return make_notebook_py(
            csv_path=analysis["csv_path"],
            contributions=analysis["contributions"],
            epsilon=analysis["epsilon"],
            columns=analysis["columns"],
        )

    @render.text
    def analysis_python_text():
        return analysis_python()

    @render.download(
        filename="dp-creator-script.py",
        media_type="text/x-python",
    )
    async def download_script():
        analysis = analysis_dict()
        script_py = make_script_py(
            contributions=analysis["contributions"],
            epsilon=analysis["epsilon"],
            columns=analysis["columns"],
        )
        yield script_py

    @render.download(
        filename="dp-creator-notebook.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook_unexecuted():
        analysis = analysis_dict()
        notebook_py = make_notebook_py(
            csv_path=analysis["csv_path"],
            contributions=analysis["contributions"],
            epsilon=analysis["epsilon"],
            columns=analysis["columns"],
        )
        notebook_nb = convert_py_to_nb(notebook_py)
        yield notebook_nb

    @render.download(
        filename="dp-creator-notebook-executed.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook_executed():
        analysis = analysis_dict()
        notebook_py = make_notebook_py(
            csv_path=analysis["csv_path"],
            contributions=analysis["contributions"],
            epsilon=analysis["epsilon"],
            columns=analysis["columns"],
        )
        notebook_nb = convert_py_to_nb(notebook_py, execute=True)
        yield notebook_nb
