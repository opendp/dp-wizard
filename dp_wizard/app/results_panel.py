from json import dumps

from shiny import ui, render

from dp_wizard.utils.templates import make_notebook_py, make_script_py
from dp_wizard.utils.converters import convert_py_to_nb


def results_ui():
    return ui.nav_panel(
        "Download results",
        ui.p("TODO: Use this information to fill in a template!"),
        ui.output_code("data_dump"),
        ui.markdown(
            "You can now make a differentially private release of your data. "
            "This will lock the configuration you’ve provided on the previous pages."
        ),
        ui.markdown("TODO: Button: “Download Report (.txt)” (implemented as yaml?)"),
        ui.markdown("TODO: Button: “Download Report (.csv)"),
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
    @render.code
    def data_dump():
        # TODO: Use this information in a template!
        return dumps(
            {
                "csv_path": csv_path(),
                "contributions": contributions(),
                "lower_bounds": lower_bounds(),
                "upper_bounds": upper_bounds(),
                "bin_counts": bin_counts(),
                "weights": weights(),
                "epsilon": epsilon(),
            },
            indent=2,
        )

    @render.download(
        filename="dp-wizard-script.py",
        media_type="text/x-python",
    )
    async def download_script():
        contributions = input.contributions()
        script_py = make_script_py(
            contributions=contributions,
            epsilon=1,
            weights=[1],
        )
        yield script_py

    @render.download(
        filename="dp-wizard-notebook.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook_unexecuted():
        contributions = input.contributions()
        notebook_py = make_notebook_py(
            csv_path="todo.csv",
            contributions=contributions,
            epsilon=1,
            weights=[1],
        )
        notebook_nb = convert_py_to_nb(notebook_py)
        yield notebook_nb

    @render.download(
        filename="dp-wizard-notebook-executed.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook_executed():
        contributions = input.contributions()
        notebook_py = make_notebook_py(
            csv_path="todo.csv",
            contributions=contributions,
            epsilon=1,
            weights=[1],
        )
        notebook_nb = convert_py_to_nb(notebook_py, execute=True)
        yield notebook_nb
