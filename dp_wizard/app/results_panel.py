from json import dumps

from shiny import ui, render, reactive

from dp_wizard.utils.templates import make_notebook_py, make_script_py
from dp_wizard.utils.converters import convert_py_to_nb


def results_ui():
    return ui.nav_panel(
        "Download results",
        ui.markdown("You can now make a differentially private release of your data."),
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
        filename="dp-wizard-script.py",
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
        filename="dp-wizard-notebook.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook():
        analysis = analysis_dict()
        notebook_py = make_notebook_py(
            csv_path=analysis["csv_path"],
            contributions=analysis["contributions"],
            epsilon=analysis["epsilon"],
            columns=analysis["columns"],
        )
        notebook_nb = convert_py_to_nb(notebook_py, execute=True)
        yield notebook_nb
